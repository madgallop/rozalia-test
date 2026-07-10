# import essential libraries 
import streamlit as st
import pandas as pd
import os
import plotly.express as px
from datetime import datetime, date
from streamlit_gsheets import GSheetsConnection

# get info from config file
from config import DEBRIS_GROUPS, METADATA_FIELDS, SUMMARY_TOTALS, DROPDOWN_OPTIONS

conn = st.connection("gsheets", type=GSheetsConnection)

# --- SYSTEM CONFIGURATION ---
DB_FILE = "master_data.csv"
ROZALIA_PALETTE = ["#7BB3CC", "#E8A85D", "#92AD94", "#A4C3B2", "#BC6C25", "#8D99AE", "#D4A373", "#788794", "#E9EDC9"]
ALL_DEBRIS_ITEMS = [item for sublist in DEBRIS_GROUPS.values() for item in sublist]

def load_and_sync_data():
    """
    Connects to Google Sheets using secrets, pulls the master log, 
    and ensures all columns exist and are formatted correctly.
    """
    try:
        conn = st.connection("gsheets", type=GSheetsConnection)
        df = conn.read(
            spreadsheet=st.secrets["connections"]["gsheets"]["spreadsheet"],
            ttl="1m"
        )

        if df is None or df.empty:
            return pd.DataFrame(columns=METADATA_FIELDS + ALL_DEBRIS_ITEMS + SUMMARY_TOTALS)

        cols_to_drop = ['Year', 'Month', 'Day']
        df = df.drop(columns=[c for c in cols_to_drop if c in df.columns])
        
        for col in METADATA_FIELDS:
            if col not in df.columns:
                df[col] = "None"
            else:
                df[col] = df[col].fillna("None").astype(str)

        numeric_cols = ALL_DEBRIS_ITEMS + SUMMARY_TOTALS
        for col in numeric_cols:
            if col not in df.columns:
                df[col] = 0
            else:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        
        existing_meta = [c for c in METADATA_FIELDS if c in df.columns] 
        existing_debris = [c for c in ALL_DEBRIS_ITEMS if c in df.columns]   
        existing_totals = [c for c in SUMMARY_TOTALS if c in df.columns]
        
        if "Date" in existing_meta:
            existing_meta.remove("Date")
        
        new_column_order = ["Date"] + existing_meta + existing_debris + existing_totals
        df = df[new_column_order]

        return df

    except Exception as e:
        st.error(f"Error connecting to Google Sheets: {e}")
        return pd.DataFrame()

st.set_page_config(page_title="Rozalia Data Dashboard", layout="wide")
df = load_and_sync_data()

if df.empty:
    st.error("Critical Error: Master Database File Missing or Corrupted.")
else:
    st.sidebar.title("ROZALIA PROJECT")
    page = st.sidebar.radio("SECTIONS", ["New Entry", "History", "Dashboard"])

    # --- SECTION 1: NEW ENTRY ---
    if page == "New Entry":
        st.title("DATA ENTRY FORM")

        st.markdown(
            """
            <style>
            div[data-testid="InputInstructions"] { display: none; }
            </style>
            """,
            unsafe_allow_html=True
        )

        st.components.v1.html(
            """
            <script>
            const doc = window.parent.document;
            doc.addEventListener('keydown', function(e) {
                if (e.keyCode === 13 && e.target.tagName !== 'TEXTAREA') {
                    e.preventDefault();
                    e.stopImmediatePropagation();
                }
            }, true);
            </script>
            """,
            height=0,
        )

        with st.form("entry_form", clear_on_submit=False):
            st.subheader("1. CLEANUP DETAILS")
            meta_in = {}
            REQUIRED_FIELDS = ["Date", "Location", "City", "State", "Country", "Name of Organization/Individual", "Email"]

            # Filter out Outlier and Submission Timestamp from manual user input fields
            fields_to_show = [f for f in METADATA_FIELDS if f not in ["Outlier", "Submission Timestamp"]]
            for i in range(0, len(fields_to_show), 3):
                row_cols = st.columns(3)
                for j, field in enumerate(fields_to_show[i:i+3]):
                    c = row_cols[j]
                    display_label = field.upper().replace("#", "NUMBER")
                    if field in REQUIRED_FIELDS:
                        display_label = f"{display_label} :red[*]"

                    f_key = f"meta_{field}"

                    if field in DROPDOWN_OPTIONS:
                        meta_in[field] = c.selectbox(display_label, options=DROPDOWN_OPTIONS[field], index=None, key=f_key)
                    elif "Date" in field:
                        meta_in[field] = c.date_input(display_label, date.today(), key=f_key)
                    elif field in ["Total weight", "Distance cleaned", "Duration (hrs)"]:
                        meta_in[field] = c.number_input(display_label, min_value=0.0, step=0.1, value=0.0, key=f_key)
                    elif "Participants" in field or "#" in field:
                        meta_in[field] = c.number_input(display_label, min_value=0, step=1, value=0, key=f_key)
                    else:
                        meta_in[field] = c.text_input(display_label, key=f_key)

            st.markdown("---")
            
            st.subheader("2. DEBRIS QUANTIFICATION")
            counts = {}
            tabs = st.tabs([k.upper() for k in DEBRIS_GROUPS.keys()])
            for i, (group_name, items) in enumerate(DEBRIS_GROUPS.items()):
                with tabs[i]:
                    d_cols = st.columns(3)
                    for j, item in enumerate(items):
                        counts[item] = d_cols[j % 3].number_input(item, min_value=0, step=1, value=0, key=f"count_{item}")

            st.markdown("---")
            
            st.subheader("3. SUBMIT ENTRY")
            st.info("**Done entering in your cleanup?**")
            submit_col1, submit_col2 = st.columns([1, 3])
            submitted = submit_col1.form_submit_button("SUBMIT DATA")

            if submitted:
                missing_fields = [r for r in REQUIRED_FIELDS if not meta_in.get(r)]
                if missing_fields:
                    st.error(f"⚠️ **Missing required fields:** {', '.join(missing_fields)}")
                else:
                    cleaned_meta = {}
                    for field, val in meta_in.items():
                        if val is not None and str(val).strip() != "":
                            cleaned_meta[field] = val
                        else:
                            cleaned_meta[field] = "None"

                    cleaned_counts = {k: (v if v is not None else 0) for k, v in counts.items()}
                    new_row = {**cleaned_meta, **cleaned_counts}
                    
                    new_row["Date"] = pd.to_datetime(meta_in["Date"]).strftime('%Y-%m-%d')
                    
                    # Track precisely when this specific entry hits the server backend
                    new_row["Submission Timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    
                    # Calculate group category sums
                    new_row["Total Plastic Items (excluding Foam)"] = sum(cleaned_counts.get(i, 0) for i in DEBRIS_GROUPS["Plastic"])
                    new_row["Total Foam Items"] = sum(cleaned_counts.get(i, 0) for i in DEBRIS_GROUPS["Foam"])
                    new_row["Total PPE Items"] = sum(cleaned_counts.get(i, 0) for i in DEBRIS_GROUPS["PPE"])
                    new_row["Total Metal Items"] = sum(cleaned_counts.get(i, 0) for i in DEBRIS_GROUPS["Metal"])
                    new_row["Total Glass/Rubber Items"] = sum(cleaned_counts.get(i, 0) for i in DEBRIS_GROUPS["Glass & Rubber"])
                    new_row["Total Paper/Cloth Items"] = sum(cleaned_counts.get(i, 0) for i in DEBRIS_GROUPS["Paper & Cloth"])
                    new_row["Total Fishing Debris Items"] = sum(cleaned_counts.get(i, 0) for i in DEBRIS_GROUPS["Fishing Debris"])
                    
                    # Direct granular references to Microplastics items from the blueprint schema
                    new_row["Total Plastic Fragments (> 30mm)"] = cleaned_counts.get("LARGE plastic >30mm", 0)
                    new_row["Total Plastic Fragments (5-30mm)"] = cleaned_counts.get("SMALL plastic 5-30mm", 0)
                    new_row["Total Microplastics (0-5mm)"] = cleaned_counts.get("Micro plastic 0-5mm", 0)
                    
                    # Miscellaneous and final cumulative math
                    new_row["Total Misc"] = sum(cleaned_counts.get(i, 0) for i in DEBRIS_GROUPS["Miscellaneous"])
                    new_row["Total (All)"] = sum(cleaned_counts.values())

                    try:
                        conn = st.connection("gsheets", type=GSheetsConnection)
                        target_url = st.secrets["connections"]["gsheets"]["spreadsheet"]
                        current_df = conn.read(spreadsheet=target_url, ttl=0)

                        new_df = pd.DataFrame([new_row])
                        if current_df is not None and not current_df.empty:
                            updated_df = pd.concat([current_df, new_df], ignore_index=True).copy()
                        else:
                            updated_df = new_df

                        allowed = METADATA_FIELDS + ALL_DEBRIS_ITEMS + SUMMARY_TOTALS
                        final_cols = [c for c in updated_df.columns if c in allowed]
                        
                        conn.update(spreadsheet=target_url, data=updated_df[final_cols])
                        
                        st.cache_data.clear()
                        st.success("Successfully saved to Master Database!")
                        st.balloons()
                        import time
                        time.sleep(2)
                        st.rerun()

                    except Exception as e:
                        st.error(f"Save Failed: {e}")

    # --- SECTION 2: HISTORY ---
    elif page == "History":
        st.title("CLEANUP DATA ARCHIVE")
        hist_df = load_and_sync_data()
        
        if not hist_df.empty:
            if "State" in hist_df.columns:
                hist_df["State"] = hist_df["State"].astype(str).str.upper()
                
            MULTIPLIER = 4.0 
            debris_stats = hist_df[ALL_DEBRIS_ITEMS].agg(['mean', 'std'])
            
            def check_outlier(row):
                for item in ALL_DEBRIS_ITEMS:
                    threshold = (MULTIPLIER * debris_stats.loc['std', item]) + debris_stats.loc['mean', item]
                    if row[item] > threshold:
                        return "O"
                return ""

            hist_df['Outlier'] = hist_df.apply(check_outlier, axis=1)
            hist_df['Date'] = pd.to_datetime(hist_df['Date'], errors='coerce')
            hist_df = hist_df.sort_values(by='Date', ascending=False)

            search_q = st.text_input("SEARCH BY LOCATION OR CITY", "").strip()
            if search_q:
                mask = (
                    hist_df['Location'].astype(str).str.contains(search_q, case=False, na=False) | 
                    hist_df['City'].astype(str).str.contains(search_q, case=False, na=False)
                )
                hist_df = hist_df[mask]

            display_df = hist_df.copy()
            display_df['Date'] = display_df['Date'].dt.strftime('%Y-%m-%d').fillna("Missing Date")

            st.markdown(f"**RECORD COUNT:** {len(display_df)}")
            st.dataframe(display_df, use_container_width=True)
            
            st.download_button(
                label="EXPORT CSV", 
                data=hist_df.to_csv(index=False).encode('utf-8-sig'), 
                file_name="cleanup_archive.csv", 
                mime="text/csv"
            )

    # --- SECTION 3: DASHBOARD ---
    elif page == "Dashboard":
        st.title("DATA DASHBOARD")

        f_df = df.copy()
        if "State" in f_df.columns:
            f_df["State"] = f_df["State"].astype(str).str.upper()
        f_df['Date'] = pd.to_datetime(f_df['Date'], errors='coerce')
        f_df['Year'] = f_df['Date'].dt.year.fillna("Unknown").astype(str)
        f_df['Month'] = f_df['Date'].dt.month_name().fillna("Unknown")

        st.markdown("### DATA CONTROLS")
        st.markdown("**STEP 1: FILTER DATA**")
        
        r1_c1, r1_c2, r1_c3, r1_c4 = st.columns(4)
        r2_c1, r2_c2, r2_c3, r2_c4 = st.columns(4)
        r3_c1, r3_c2, r3_c3, r3_c4 = st.columns(4)
        
        state_opts = sorted(f_df["State"].dropna().unique().astype(str))
        sel_states = r1_c1.multiselect("SELECT STATE", options=state_opts)
        if sel_states:
            f_df = f_df[f_df["State"].isin(sel_states)]

        city_opts = sorted(f_df["City"].dropna().unique().astype(str))
        sel_cities = r1_c2.multiselect("SELECT CITY", options=city_opts)
        if sel_cities:
            f_df = f_df[f_df["City"].isin(sel_cities)]

        loc_opts = sorted(f_df["Location"].dropna().unique().astype(str))
        sel_locs = r1_c3.multiselect("SELECT LOCATION", options=loc_opts)
        if sel_locs:
            f_df = f_df[f_df["Location"].isin(sel_locs)]

        year_opts = sorted(f_df["Year"].dropna().unique())
        sel_years = r1_c4.multiselect("SELECT YEAR", options=year_opts)
        if sel_years:
            f_df = f_df[f_df["Year"].isin(sel_years)]

        month_opts = sorted(f_df["Month"].dropna().unique())
        sel_months = r2_c1.multiselect("SELECT MONTH", options=month_opts)
        if sel_months:
            f_df = f_df[f_df["Month"].isin(sel_months)]

        cleanup_opts = sorted(f_df["Type of cleanup"].dropna().unique().astype(str))
        sel_cleanup = r2_c2.multiselect("SELECT TYPE OF CLEANUP", options=cleanup_opts)
        if sel_cleanup:
            f_df = f_df[f_df["Type of cleanup"].isin(sel_cleanup)]

        type_loc_col = "Type of location (i.e. Sandy Beach, Marina, Open Water)"
        type_loc_opts = sorted(f_df[type_loc_col].dropna().unique().astype(str)) if type_loc_col in f_df.columns else []
        sel_type_loc = r2_c3.multiselect("SELECT TYPE OF LOCATION", options=type_loc_opts)
        if sel_type_loc and type_loc_col in f_df.columns:
            f_df = f_df[f_df[type_loc_col].isin(sel_type_loc)]

        # Updated to query the precise field key mapping name without crashing
        org_col = "Name of Organization/Individual"
        org_opts = sorted(f_df[org_col].dropna().unique().astype(str))
        sel_orgs = r3_c1.multiselect("SELECT ORGANIZATION/INDIVIDUAL", options=org_opts)
        if sel_orgs:
            f_df = f_df[f_df[org_col].isin(sel_orgs)]

        st.markdown("**STEP 2: GROUP DATA BY**")
        group_options = ["Year", "Month", "State", "Type of cleanup"]
        selected_groups = st.multiselect("GROUP BY:", options=group_options, default=["Year"], label_visibility="collapsed")

        if f_df.empty or not selected_groups:
            st.warning("No records match these filters or no grouping selected.")
        else:
            f_df['X_Axis'] = f_df[selected_groups].astype(str).agg(' | '.join, axis=1)
            
            total_pieces = int(f_df[ALL_DEBRIS_ITEMS].sum().sum())
            m1, m2, m3 = st.columns(3)
            m1.metric("CLEANUPS", f"{len(f_df):,}")
            m2.metric("TOTAL PIECES", f"{total_pieces:,}")
            m3.metric("AVG PIECES", f"{int(total_pieces / len(f_df)) if len(f_df) > 0 else 0:,}")

            tab_main, tab_sub = st.tabs(["TOTAL COLLECTIONS", "SUBCATEGORY BREAKDOWNS"])

            with tab_main:
                st.subheader("MATERIAL TYPE")
                cat_data = []
                for cat, items in DEBRIS_GROUPS.items():
                    valid_items = [i for i in items if i in f_df.columns]
                    if valid_items:
                        cat_sum = f_df.groupby('X_Axis')[valid_items].sum().sum(axis=1).reset_index(name='Count')
                        cat_sum['Material'] = cat
                        cat_data.append(cat_sum)
                
                plot_df = pd.concat(cat_data)
                main_chart_type = st.radio("VIEW TOTALS AS:", ["Stacked Bar", "Pie Chart"], horizontal=True, key="main_toggle")

                if main_chart_type == "Pie Chart":
                    pie_df = plot_df.groupby('Material')['Count'].sum().reset_index()
                    pie_df = pie_df[pie_df['Count'] > 0] 
                    fig_stack = px.pie(pie_df, values='Count', names='Material', hole=0.4, template="simple_white", color_discrete_sequence=ROZALIA_PALETTE)
                    fig_stack.update_traces(hovertemplate="<b>%{label}</b><br>Total: %{value:,}<extra></extra>")
                else:
                    fig_stack = px.bar(plot_df, x='X_Axis', y='Count', color='Material', template="simple_white", color_discrete_sequence=ROZALIA_PALETTE, barmode='stack', category_orders={"X_Axis": sorted(plot_df['X_Axis'].unique())}, custom_data=[plot_df['Count']])
                    fig_stack.update_traces(hovertemplate="<b>%{fullData.name}</b><br>Total: %{customdata[0]:,} pieces<br>Share: %{y:.1f}%<extra></extra>")
                    fig_stack.update_layout(barnorm='percent', yaxis_title="PROPORTION (%)")

                fig_stack.update_layout(xaxis_title=None, font_family="Avenir")
                st.plotly_chart(fig_stack, use_container_width=True)

            with tab_sub:
                st.subheader("SUBCATEGORY BREAKDOWNS")
                target_cat = st.selectbox("CHOOSE A SUBCATEGORY:", options=list(DEBRIS_GROUPS.keys()))
                sub_items = [i for i in DEBRIS_GROUPS[target_cat] if i in f_df.columns]
                
                item_counts = f_df[sub_items].sum()
                active_items = item_counts[item_counts > 0].index.tolist()

                if not active_items:
                    st.info(f"No active {target_cat} items found for this selection.")
                else:
                    sub_df = f_df.melt(id_vars=['X_Axis'], value_vars=active_items, var_name='Item', value_name='Count')
                    sub_df = sub_df.groupby(['X_Axis', 'Item'])['Count'].sum().reset_index()
                    sub_total = sub_df['Count'].sum()

                    st.markdown(f"**Total {target_cat} pieces found: {int(sub_total):,}**")
                    chart_type = st.radio("VIEW AS:", ["Stacked Bar", "Pie Chart"], horizontal=True, key="sub_toggle")

                    if chart_type == "Pie Chart":
                        pie_sub_df = sub_df.groupby('Item')['Count'].sum().reset_index()
                        fig_sub = px.pie(pie_sub_df, values='Count', names='Item', hole=0.4, color_discrete_sequence=ROZALIA_PALETTE)
                        fig_sub.update_layout(annotations=[dict(text=f'{int(sub_total):,}<br>total', x=0.5, y=0.5, font_size=20, showarrow=False)])
                        fig_sub.update_traces(hovertemplate="<b>%{label}</b><br>Count: %{value:,} pieces<br>%{percent}<extra></extra>")
                    else:
                        # Fixed the length-mismatch crash logic by passing custom_data directly into the constructor
                        fig_sub = px.bar(
                            sub_df, x='X_Axis', y='Count', color='Item',
                            template="simple_white", color_discrete_sequence=ROZALIA_PALETTE,
                            category_orders={"X_Axis": sorted(sub_df['X_Axis'].unique())},
                            custom_data=['Count']
                        )
                        fig_sub.update_layout(barnorm='percent', yaxis_title="PROPORTION (%)")
                        fig_sub.update_traces(hovertemplate="<b>%{fullData.name}</b><br>Count: %{customdata[0]:,} pieces<br>Share: %{y:.1f}%<extra></extra>")
                    
                    fig_sub.update_layout(xaxis_title=None, font_family="Avenir")
                    st.plotly_chart(fig_sub, use_container_width=True)

            st.markdown("---")
            with st.expander("View tabular data for this selection"):
                preview_df = f_df.copy()
                if 'Date' in preview_df.columns:
                    preview_df['Date'] = preview_df['Date'].dt.strftime('%Y-%m-%d').fillna("Unknown")
                st.dataframe(preview_df, use_container_width=True)
                
                st.download_button(
                    label="DOWNLOAD FILTERED CSV",
                    data=preview_df.to_csv(index=False).encode('utf-8-sig'),
                    file_name="filtered_cleanup_data.csv",
                    mime="text/csv"
                )