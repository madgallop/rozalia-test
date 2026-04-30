#import essential libraries 
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
        # 1. Establish the connection to Google Sheets
        conn = st.connection("gsheets", type=GSheetsConnection)
        
        # 2. Read the data using the URL stored in your secrets
        # ttl="1m" caches data for 60 seconds to improve performance
        df = conn.read(
            spreadsheet=st.secrets["connections"]["gsheets"]["spreadsheet"],
            ttl="1m"
        )

        # 3. Handle Empty Sheets
        if df is None or df.empty:
            # Return a blank dataframe with the correct structure so the app doesn't crash
            return pd.DataFrame(columns=METADATA_FIELDS + ALL_DEBRIS_ITEMS + SUMMARY_TOTALS + ["Date"])

        # 4. Data Cleaning: Remove unwanted columns if they exist
        cols_to_drop = ['Year', 'Month', 'Day']
        df = df.drop(columns=[c for c in cols_to_drop if c in df.columns])
        
        # 5. Metadata Repair: Ensure all expected metadata columns exist
        for col in METADATA_FIELDS:
            if col not in df.columns:
                df[col] = "None"
            else:
                # Fill empty cells in metadata with "None" string
                df[col] = df[col].fillna("None").astype(str)

        # 6. Debris & Totals Repair: Ensure count columns exist and are numeric
        numeric_cols = ALL_DEBRIS_ITEMS + SUMMARY_TOTALS
        for col in numeric_cols:
            if col not in df.columns:
                df[col] = 0
            else:
                # Convert to numbers; 'coerce' turns typos into 0
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

        # 7. Date Formatting: Mandatory for the Dashboard filters to work
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        
        # 8. Final Reordering: Maintain a consistent structure
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

        # 1. This CSS hides the "Press Enter to submit" help text 
        st.markdown(
            """
            <style>
            div[data-testid="InputInstructions"] {
                display: none;
            }
            </style>
            """,
            unsafe_allow_html=True
        )

        # This CSS/JS snippet prevents 'Enter' from submitting the form
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


        
        # We use clear_on_submit=False so data isn't wiped if there is a validation error
        with st.form("entry_form", clear_on_submit=False):
            # 1. METADATA SECTION
            st.subheader("1. CLEANUP DETAILS")
            meta_in = {}
            REQUIRED_FIELDS = ["Date", "Location", "City", "State", "Country"]

            fields_to_show = [f for f in METADATA_FIELDS if f != "Outlier"]
            for i in range(0, len(fields_to_show), 3):
                row_cols = st.columns(3)
                for j, field in enumerate(fields_to_show[i:i+3]):
                    c = row_cols[j]
                    display_label = field.upper().replace("#", "NUMBER")
                    if field in REQUIRED_FIELDS:
                        display_label = f"{display_label} :red[*]"

                    # Logic: We use 'key' to tie these to session state so they persist
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
            
            # 2. DEBRIS SECTION
            st.subheader("2. DEBRIS QUANTIFICATION")
            counts = {}
            tabs = st.tabs([k.upper() for k in DEBRIS_GROUPS.keys()])
            for i, (group_name, items) in enumerate(DEBRIS_GROUPS.items()):
                with tabs[i]:
                    d_cols = st.columns(3)
                    for j, item in enumerate(items):
                        # Unique key for every debris item to ensure persistence
                        counts[item] = d_cols[j % 3].number_input(item, min_value=0, step=1, value=0, key=f"count_{item}")

            st.markdown("---")
            
            # 3. FINALIZATION SECTION
            st.subheader("3. SUBMIT ENTRY")
            st.info("**Done entering in your cleanup?**")
            
            submit_col1, submit_col2 = st.columns([1, 3])
            submitted = submit_col1.form_submit_button("SUBMIT DATA")

            st.markdown("*Navigate to History to view data*")


            if submitted:
                # 1. Validation Check: Ensure required fields aren't empty
                missing_fields = [r for r in REQUIRED_FIELDS if not meta_in.get(r)]
                
                if missing_fields:
                    st.error(f"⚠️ **Missing required fields:** {', '.join(missing_fields)}")
                else:
                    # 2. PREPARE METADATA
                    cleaned_meta = {}
                    for field, val in meta_in.items():
                        if val is not None and str(val).strip() != "":
                            cleaned_meta[field] = val
                        else:
                            cleaned_meta[field] = "None"

                    # 3. PREPARE DEBRIS COUNTS
                    cleaned_counts = {k: (v if v is not None else 0) for k, v in counts.items()}
                    
                    # 4. MERGE INTO NEW ROW
                    new_row = {**cleaned_meta, **cleaned_counts}
                    
                    # Format the date properly for Google Sheets (YYYY-MM-DD)
                    new_row["Date"] = pd.to_datetime(meta_in["Date"]).strftime('%Y-%m-%d')
                    
                    # 5. CALCULATE TOTALS
                    category_to_total_col = {
                        "Plastic": "Total Plastic", "Foam": "Total Foam", "PPE": "Total PPE",
                        "Metal": "Total Metal", "Glass & Rubber": "Total Glass & Rubber",
                        "Paper & Cloth": "Total Paper & Cloth", "Fishing Debris": "Total Fishing Debris",
                        "Microplastics & Fibers": "Total Microplastics"
                    }

                    grand_total = 0
                    for group_name, total_col in category_to_total_col.items():
                        group_sum = sum(cleaned_counts.get(item, 0) for item in DEBRIS_GROUPS.get(group_name, []))
                        new_row[total_col] = group_sum
                        grand_total += group_sum
                    
                    # Add 'Other' category and Grand Total
                    other_sum = sum(cleaned_counts.get(item, 0) for item in DEBRIS_GROUPS.get("Other", []))
                    grand_total += other_sum
                    new_row["Grand Total"] = grand_total

                    # --- DEBUG SECTION ---
                    print("--- DEBUGGING CONNECTION ---")
                    print(f"Spreadsheet URL in secrets: {'Found' if 'spreadsheet' in st.secrets['connections']['gsheets'] else 'MISSING'}")
                    print(f"Private Key in secrets: {'Found' if 'private_key' in st.secrets['connections']['gsheets'] else 'MISSING'}")
                    print(f"Service Account Email: {st.secrets['connections']['gsheets'].get('client_email', 'NOT FOUND')}")
                    # ---------------------

                    # 6. SAVE TO GOOGLE SHEETS
# 6. SAVE TO GOOGLE SHEETS (DEEP DEBUG VERSION)
                    try:
                        print("\n" + "="*50)
                        print(" DEBUG: STARTING SAVE PROCESS")
                        
                        # 1. Check Secret Keys Presence
                        gsheets_secrets = st.secrets.get("connections", {}).get("gsheets", {})
                        print(f"DEBUG: 'gsheets' keys found: {list(gsheets_secrets.keys())}")
                        
                        # 2. Check for the 'type' field inside secrets
                        # If this is missing or wrong, the library defaults to 'Public'
                        secret_type = gsheets_secrets.get("type")
                        print(f"DEBUG: Secret 'type' value: {secret_type}")

                        # 3. Establish connection
                        conn = st.connection("gsheets", type=GSheetsConnection)
                        
                        # 4. Inspect the internal 'client' type
                        # This is the most important check. It tells us which class is being used.
                        internal_client = type(conn._instance).__name__
                        print(f"DEBUG: Internal Client Class: {internal_client}")
                        
                        if internal_client == "GSheetsPublicSpreadsheetClient":
                            print("⚠️ ALERT: Library is still defaulting to PUBLIC mode.")
                        else:
                            print("✅ SUCCESS: Library is using SERVICE ACCOUNT mode.")

                        target_url = st.secrets["connections"]["gsheets"]["spreadsheet"]
                        print(f"DEBUG: Target URL: {target_url[:30]}...")

                        # 5. Attempt Read
                        print("DEBUG: Attempting to pull current data...")
                        current_df = conn.read(spreadsheet=target_url, ttl=0)
                        print(f"DEBUG: Read successful. Current rows: {len(current_df) if current_df is not None else 0}")

                        # 6. Prepare and Append
                        new_df = pd.DataFrame([new_row])
                        if current_df is not None and not current_df.empty:
                            updated_df = pd.concat([current_df, new_df], ignore_index=True).copy()
                        else:
                            updated_df = new_df

                        # 7. Attempt Update
                        print("DEBUG: Launching conn.update()...")
                        allowed = METADATA_FIELDS + ALL_DEBRIS_ITEMS + SUMMARY_TOTALS + ["Date"]
                        final_cols = [c for c in updated_df.columns if c in allowed]
                        
                        conn.update(spreadsheet=target_url, data=updated_df[final_cols])
                        
                        print("✅ DEBUG: conn.update() finished without error.")
                        print("="*50 + "\n")

                        st.cache_data.clear()
                        st.success("Successfully saved to Master Database!")
                        st.balloons()
                        
                        import time
                        time.sleep(2)
                        st.rerun()

                    except Exception as e:
                        print(f"❌ DEBUG: CRASH DETECTED")
                        print(f"Error Type: {type(e).__name__}")
                        print(f"Error Message: {e}")
                        import traceback
                        print("Full Traceback:")
                        traceback.print_exc()
                        print("="*50 + "\n")
                        st.error(f"Save Failed: {e}")

    # --- SECTION 2: HISTORY ---
    elif page == "History":
        st.title("CLEANUP DATA ARCHIVE")
        hist_df = load_and_sync_data()
        
        if not hist_df.empty:
            if "State" in hist_df.columns:
                hist_df["State"] = hist_df["State"].astype(str).str.upper()
            # 1. Statistical Outlier Calculation (Replicating your Excel Formula)
            # Change this multiplier to match your $GJ$2 value (usually 2 or 3)
            MULTIPLIER = 4.0 
            
            # Calculate stats for all debris items across the whole dataset
            debris_stats = hist_df[ALL_DEBRIS_ITEMS].agg(['mean', 'std'])
            
            def check_outlier(row):
                for item in ALL_DEBRIS_ITEMS:
                    threshold = (MULTIPLIER * debris_stats.loc['std', item]) + debris_stats.loc['mean', item]
                    if row[item] > threshold:
                        return "O"
                return ""

            # Apply the logic to create the Outlier column
            hist_df['Outlier'] = hist_df.apply(check_outlier, axis=1)

            # 3. Clean up Date and Search
            hist_df['Date'] = pd.to_datetime(hist_df['Date'], errors='coerce')
            hist_df = hist_df.sort_values(by='Date', ascending=False)

            search_q = st.text_input("SEARCH BY LOCATION OR CITY", "").strip()
            if search_q:
                mask = (
                    hist_df['Location'].astype(str).str.contains(search_q, case=False, na=False) | 
                    hist_df['City'].astype(str).str.contains(search_q, case=False, na=False)
                )
                hist_df = hist_df[mask]

            # 4. Display Formatting
            display_df = hist_df.copy()
            display_df['Date'] = display_df['Date'].dt.strftime('%Y-%m-%d').fillna("Missing Date")

            st.markdown(f"**RECORD COUNT:** {len(display_df)}")
            st.markdown("*Click on any column header to sort the dataset.*")
            

            st.dataframe(display_df, use_container_width=True)
            
            # Download
            st.download_button(
                label="EXPORT CSV", 
                data=hist_df.to_csv(index=False).encode('utf-8-sig'), 
                file_name="cleanup_archive.csv", 
                mime="text/csv"
            )

            st.markdown("*Navigate to Dashboard to filter and visualize data*")




# --- SECTION 3: DASHBOARD ---
    elif page == "Dashboard":
        st.title("DATA DASHBOARD")

        # 1. Efficient Data Preparation
        f_df = df.copy()
        if "State" in f_df.columns:
            f_df["State"] = f_df["State"].astype(str).str.upper()
        f_df['Date'] = pd.to_datetime(f_df['Date'], errors='coerce')
        f_df['Year'] = f_df['Date'].dt.year.fillna("Unknown").astype(str)
        f_df['Month'] = f_df['Date'].dt.month_name().fillna("Unknown")

        # --- STEP 0: TOP DATA CHARTS ---
        # (Keep your existing Top Data Charts code here...)

        # --- STEP 1: FILTER DATA ---
        st.markdown("### DATA CONTROLS")
        st.markdown("**STEP 1: FILTER DATA**")
        
        # We define the grid exactly like your original, but handle City/Location specially
        r1_c1, r1_c2, r1_c3, r1_c4 = st.columns(4)
        r2_c1, r2_c2, r2_c3, r2_c4 = st.columns(4)
        r3_c1, r3_c2, r3_c3, r3_c4 = st.columns(4)
        
        # ROW 1: Geography & Time
        # State
        state_opts = sorted(f_df["State"].dropna().unique().astype(str))
        sel_states = r1_c1.multiselect("SELECT STATE", options=state_opts)
        if sel_states:
            f_df = f_df[f_df["State"].isin(sel_states)]

        # City (The Parent)
        city_opts = sorted(f_df["City"].dropna().unique().astype(str))
        sel_cities = r1_c2.multiselect("SELECT CITY", options=city_opts)
        if sel_cities:
            f_df = f_df[f_df["City"].isin(sel_cities)]

        # Location (The Child - filtered by City)
        loc_opts = sorted(f_df["Location"].dropna().unique().astype(str))
        sel_locs = r1_c3.multiselect("SELECT LOCATION", options=loc_opts)
        if sel_locs:
            f_df = f_df[f_df["Location"].isin(sel_locs)]

        # Year
        year_opts = sorted(f_df["Year"].dropna().unique())
        sel_years = r1_c4.multiselect("SELECT YEAR", options=year_opts)
        if sel_years:
            f_df = f_df[f_df["Year"].isin(sel_years)]

        # ROW 2: Cleanup Details & Weather
        # Month
        month_opts = sorted(f_df["Month"].dropna().unique())
        sel_months = r2_c1.multiselect("SELECT MONTH", options=month_opts)
        if sel_months:
            f_df = f_df[f_df["Month"].isin(sel_months)]

        # Type of cleanup
        cleanup_opts = sorted(f_df["Type of cleanup"].dropna().unique().astype(str))
        sel_cleanup = r2_c2.multiselect("SELECT TYPE OF CLEANUP", options=cleanup_opts)
        if sel_cleanup:
            f_df = f_df[f_df["Type of cleanup"].isin(sel_cleanup)]

        # Type of location
        type_loc_opts = sorted(f_df["Type of location"].dropna().unique().astype(str))
        sel_type_loc = r2_c3.multiselect("SELECT TYPE OF LOCATION", options=type_loc_opts)
        if sel_type_loc:
            f_df = f_df[f_df["Type of location"].isin(sel_type_loc)]

        # Weather
        weather_opts = sorted(f_df["Current Weather"].dropna().unique().astype(str))
        sel_weather = r2_c4.multiselect("SELECT WEATHER", options=weather_opts)
        if sel_weather:
            f_df = f_df[f_df["Current Weather"].isin(sel_weather)]

        # Organization
        org_opts = sorted(f_df["Organization/Individual"].dropna().unique().astype(str))
        sel_orgs = r3_c1.multiselect("SELECT ORGANIZATION/INDIVIDUAL", options=org_opts)
        if sel_orgs:
            f_df = f_df[f_df["Organization/Individual"].isin(sel_orgs)]

        # --- STEP 2: VIEW DIMENSIONS ---
        st.markdown("**STEP 2: GROUP DATA BY**")
        group_options = ["Year", "Month", "State", "Type of cleanup", "Type of location"]
        selected_groups = st.multiselect("GROUP BY:", options=group_options, default=["Year"], label_visibility="collapsed")

        if f_df.empty or not selected_groups:
            st.warning("No records match these filters or no grouping selected.")
        else:
            # Create a combined X-Axis label once
            f_df['X_Axis'] = f_df[selected_groups].astype(str).agg(' | '.join, axis=1)
            
            # Metrics
            total_pieces = int(f_df[ALL_DEBRIS_ITEMS].sum().sum())
            m1, m2, m3 = st.columns(3)
            m1.metric("CLEANUPS", f"{len(f_df):,}")
            m2.metric("TOTAL PIECES", f"{total_pieces:,}")
            m3.metric("AVG PIECES", f"{int(total_pieces / len(f_df)) if len(f_df) > 0 else 0:,}")

            tab_main, tab_sub = st.tabs(["TOTAL COLLECTIONS", "SUBCATEGORY BREAKDOWNS"])

            with tab_main:
                st.subheader("MATERIAL TYPE")
                
                # 1. Prepare Data
                cat_data = []
                for cat, items in DEBRIS_GROUPS.items():
                    valid_items = [i for i in items if i in f_df.columns]
                    if valid_items:
                        cat_sum = f_df.groupby('X_Axis')[valid_items].sum().sum(axis=1).reset_index(name='Count')
                        cat_sum['Material'] = cat
                        cat_data.append(cat_sum)
                
                plot_df = pd.concat(cat_data)

                # 2. Toggle View
                main_chart_type = st.radio("VIEW TOTALS AS:", ["Stacked Bar", "Pie Chart"], horizontal=True, key="main_toggle")

                if main_chart_type == "Pie Chart":
                    # Sum up counts and FILTER OUT ZEROS
                    pie_df = plot_df.groupby('Material')['Count'].sum().reset_index()
                    pie_df = pie_df[pie_df['Count'] > 0] 
                    
                    fig_stack = px.pie(
                        pie_df, values='Count', names='Material',
                        hole=0.4,
                        template="simple_white",
                        color_discrete_sequence=ROZALIA_PALETTE
                    )
                    fig_stack.update_traces(
                        hovertemplate="<b>%{label}</b><br>Total: %{value:,}<extra></extra>"
                    )
                else:
                    # Your original Stacked Bar logic
                    fig_stack = px.bar(
                        plot_df, x='X_Axis', y='Count', color='Material',
                        template="simple_white",
                        color_discrete_sequence=ROZALIA_PALETTE,
                        barmode='stack',
                        category_orders={"X_Axis": sorted(plot_df['X_Axis'].unique())},
                        custom_data=[plot_df['Count']]
                    )
                    fig_stack.update_traces(
                        hovertemplate="<b>%{fullData.name}</b><br>Total: %{customdata[0]:,} pieces<br>Share: %{y:.1f}%<extra></extra>"
                    )
                    fig_stack.update_layout(barnorm='percent', yaxis_title="PROPORTION (%)")

                fig_stack.update_layout(xaxis_title=None, font_family="Avenir")
                st.plotly_chart(fig_stack, use_container_width=True)

            with tab_sub:
                st.subheader("SUBCATEGORY BREAKDOWNS")
                target_cat = st.selectbox("CHOOSE A SUBCATEGORY:", options=list(DEBRIS_GROUPS.keys()))
                sub_items = [i for i in DEBRIS_GROUPS[target_cat] if i in f_df.columns]
                
                # Filter out items with 0 counts to keep the chart clean
                item_counts = f_df[sub_items].sum()
                active_items = item_counts[item_counts > 0].index.tolist()

                if not active_items:
                    st.info(f"No {target_cat} items found for this selection.")
                else:
                    sub_df = f_df.melt(id_vars=['X_Axis'], value_vars=active_items, var_name='Item', value_name='Count')
                    sub_df = sub_df.groupby(['X_Axis', 'Item'])['Count'].sum().reset_index()
                    
                    # Calculate the total for JUST this subcategory
                    sub_total = sub_df['Count'].sum()

                    # Show the total piece count for this category selection
                    st.markdown(f"**Total {target_cat} pieces found: {int(sub_total):,}**")

                    chart_type = st.radio("VIEW AS:", ["Stacked Bar", "Pie Chart"], horizontal=True, key="sub_toggle")

                    if chart_type == "Pie Chart":
                        # Group by Item for a clean category-wide Pie
                        pie_sub_df = sub_df.groupby('Item')['Count'].sum().reset_index()
                        
                        fig_sub = px.pie(pie_sub_df, values='Count', names='Item', hole=0.4,
                                         color_discrete_sequence=ROZALIA_PALETTE)
                        
                        # Add the sub-total to the center of the Donut
                        fig_sub.update_layout(
                            annotations=[dict(text=f'{int(sub_total):,}<br>total', x=0.5, y=0.5, font_size=20, showarrow=False)]
                        )
                        
                        fig_sub.update_traces(
                            hovertemplate="<b>%{label}</b><br>Count: %{value:,} pieces<br>%{percent}<extra></extra>"
                        )
                    else:
                        fig_sub = px.bar(sub_df, x='X_Axis', y='Count', color='Item',
                                         template="simple_white", color_discrete_sequence=ROZALIA_PALETTE,
                                         category_orders={"X_Axis": sorted(sub_df['X_Axis'].unique())})
                        fig_sub.update_layout(barnorm='percent', yaxis_title="PROPORTION (%)")
                        fig_sub.update_traces(
                            hovertemplate="<b>%{fullData.name}</b><br>Count: %{customdata[0]:,} pieces<br>Share: %{y:.1f}%<extra></extra>",
                            customdata=sub_df[['Count']] 
                        )
                    
                    fig_sub.update_layout(xaxis_title=None, font_family="Avenir")
                    st.plotly_chart(fig_sub, use_container_width=True)

                    # --- STEP 3: DATA PREVIEW ---
            st.markdown("---")
            with st.expander("View tabular data for this selection"):
                st.write(f"Showing the **{len(f_df)}** records used to generate the charts above.")
                
                # Format the date for display just like you did in History
                preview_df = f_df.copy()
                if 'Date' in preview_df.columns:
                    preview_df['Date'] = preview_df['Date'].dt.strftime('%Y-%m-%d').fillna("Unknown")
                
                # Display the dataframe
                st.dataframe(preview_df, use_container_width=True)
                
                # Allow them to download just this filtered slice
                st.download_button(
                    label="DOWNLOAD FILTERED CSV",
                    data=preview_df.to_csv(index=False).encode('utf-8-sig'),
                    file_name="filtered_cleanup_data.csv",
                    mime="text/csv"
                )