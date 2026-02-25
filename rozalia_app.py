import streamlit as st
import pandas as pd
import os
import plotly.express as px
from datetime import datetime, date
from config import DEBRIS_GROUPS, METADATA_FIELDS, DROPDOWN_OPTIONS

# --- SYSTEM CONFIGURATION ---
DB_FILE = "master_data.csv"
ALL_DEBRIS_ITEMS = [item for sublist in DEBRIS_GROUPS.values() for item in sublist]

ROZALIA_PALETTE = ["#7BB3CC", "#E8A85D", "#92AD94", "#A4C3B2", "#BC6C25", "#8D99AE", "#D4A373", "#788794", "#E9EDC9"]

def load_and_sync_data():
    if not os.path.exists(DB_FILE):
        return pd.DataFrame()
    
    df = pd.read_csv(DB_FILE, low_memory=False)
    
    # 1. Standardize Dates & remove timestamps
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')

    # 2. DROP Unwanted Columns
    cols_to_drop = ['Year', 'Month', 'Day', 'Latitude', 'Longitude']
    df.drop(columns=[c for c in cols_to_drop if c in df.columns], inplace=True)
    
    # 3. FIX WIND DUPLICATE
    if 'Weather (wind knots)' in df.columns:
        if 'Wind (knots) 0 if none' in df.columns:
            df['Wind (knots) 0 if none'] = df['Wind (knots) 0 if none'].replace(0, pd.NA).fillna(df['Weather (wind knots)']).fillna(0)
        else:
            df['Wind (knots) 0 if none'] = df['Weather (wind knots)']
        df.drop(columns=['Weather (wind knots)'], inplace=True)

    # 4. SAFE RENAME for Tide and Events
    rename_map = {"Tide": "State of Tide", "Recent events": "Recent events (human)"}
    for old_name, new_name in rename_map.items():
        if old_name in df.columns:
            if new_name not in df.columns:
                df.rename(columns={old_name: new_name}, inplace=True)
            else:
                df.drop(columns=[old_name], inplace=True)
    
    # 5. Define Column Groups for Reordering
    core_info = ['Date', 'Location', 'City', 'State']
    
    qualitative_meta = [
        'Type of cleanup', 'Type of location', 'Weather', 'Wind (knots) 0 if none',
        'Recent weather', 'State of Tide', 'Flow', 'Recent events (human)',
        'Distance cleaned (miles)', 'Duration (hrs)', 'Start time', 'End time',
        '# of participants', 'Total weight (lb)', 'Unusual items', 'Notes/comments'
    ]

    # 6. Apply formatting and fill missing columns
    all_meta = core_info + qualitative_meta
    for col in all_meta:
        if col not in df.columns:
            df[col] = 0 if any(x in col for x in ['lb', 'miles', 'hrs', '#', 'knots']) else "Unknown"
        elif col in ['State', 'City', 'Type of cleanup', 'Type of location', 'Weather', 'Recent weather', 'State of Tide', 'Flow', 'Recent events (human)']:
            df[col] = df[col].fillna("Unknown").astype(str).replace(["nan", ""], "Unknown")
        elif col in ['Distance cleaned (miles)', 'Duration (hrs)', 'Wind (knots) 0 if none', 'Total weight (lb)', '# of participants']:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

    for col in ALL_DEBRIS_ITEMS:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        else:
            df[col] = 0

    # 7. FINAL REORDERING
    existing_core = [c for c in core_info if c in df.columns]
    existing_qual = [c for c in qualitative_meta if c in df.columns]
    existing_debris = [c for c in ALL_DEBRIS_ITEMS if c in df.columns]
    
    remaining_cols = [c for c in df.columns if c not in existing_core + existing_qual + existing_debris]
    
    new_column_order = existing_core + existing_qual + existing_debris + remaining_cols
    df = df[new_column_order]

    # 8. Clean up Date display (removes 00:00:00)
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')    
    return df

st.set_page_config(page_title="Rozalia Archive", layout="wide")
df = load_and_sync_data()

if df.empty:
    st.error("Critical Error: Master Database File Missing or Corrupted.")
else:
    st.sidebar.title("ROZALIA PROJECT")
    page = st.sidebar.radio("SECTIONS", ["New Entry", "History", "Dashboard"])

    # --- SECTION 1: NEW ENTRY ---
    if page == "New Entry":
        st.title("DATA ENTRY FORM")
        with st.form("entry_form", clear_on_submit=True):
            st.subheader("METADATA")
            meta_in = {}
            cols = st.columns(3)
            for i, field in enumerate(METADATA_FIELDS):
                c = cols[i % 3]
                if field in DROPDOWN_OPTIONS:
                    meta_in[field] = c.selectbox(field.upper(), options=DROPDOWN_OPTIONS[field], index=None)
                elif "Date" in field:
                    meta_in[field] = c.date_input(field.upper(), date.today())
                elif any(x in field for x in ["Latitude", "Longitude", "Total weight", "Distance", "Duration", "#"]):
                    meta_in[field] = c.number_input(field.upper(), value=0.0)
                else:
                    meta_in[field] = c.text_input(field.upper())

            st.markdown("---")
            st.subheader("DEBRIS QUANTIFICATION")
            counts = {}
            tabs = st.tabs([k.upper() for k in DEBRIS_GROUPS.keys()])
            for i, group in enumerate(DEBRIS_GROUPS.keys()):
                with tabs[i]:
                    items = DEBRIS_GROUPS[group]
                    d_cols = st.columns(3)
                    for j, item in enumerate(items):
                        counts[item] = d_cols[j % 3].number_input(item, min_value=0, step=1, value=0)

            if st.form_submit_button("COMMIT TO MASTER LOG"):
                if not meta_in.get("Location") or not meta_in.get("City"):
                    st.warning("Incomplete Data: Location and City fields are mandatory.")
                else:
                    # 1. Load existing data
                    current_df = load_and_sync_data()
                    
                    # 2. Prepare the new row
                    new_row = {**meta_in, **counts}
                    new_row["Date"] = pd.to_datetime(meta_in["Date"])

                    # 3. CALCULATE SUBTOTALS ON THE FLY
                    # This maps your internal groups to your specific CSV Column Names
                    
                    # Plastic Total
                    new_row["Plastic Total"] = sum(counts.get(i, 0) for i in DEBRIS_GROUPS.get("Plastic", []))
                    
                    # PPE Total
                    new_row["PPE Total"] = sum(counts.get(i, 0) for i in DEBRIS_GROUPS.get("PPE", []))
                    
                    # Metal Total
                    new_row["Metal Total"] = sum(counts.get(i, 0) for i in DEBRIS_GROUPS.get("Metal", []))
                    
                    # Glass/Rubber Total
                    gr_items = DEBRIS_GROUPS.get("Glass & Rubber", [])
                    new_row["Glass/Rubber Total"] = sum(counts.get(i, 0) for i in gr_items)
                    
                    # Paper/Cloth Total
                    pc_items = DEBRIS_GROUPS.get("Paper & Cloth", [])
                    new_row["Paper/Cloth Total"] = sum(counts.get(i, 0) for i in pc_items)
                    
                    # Fishing Debris Total
                    new_row["Fishing Debris Total"] = sum(counts.get(i, 0) for i in DEBRIS_GROUPS.get("Fishing Debris", []))
                    
                    # Micro/Fibers Total
                    micro_items = DEBRIS_GROUPS.get("Microplastics & Fibers", [])
                    new_row["Microplastics, Fibers, Fragments Total"] = sum(counts.get(i, 0) for i in micro_items)
                    
                    # Foam Total
                    new_row["Foam Total"] = sum(counts.get(i, 0) for i in DEBRIS_GROUPS.get("Foam", []))
                    
                    # Other Total
                    new_row["Other Total"] = sum(counts.get(i, 0) for i in DEBRIS_GROUPS.get("Other", []))

                    # 4. CALCULATE GRAND TOTAL
                    # This adds up all the subtotals we just created
                    totals_to_sum = [
                        "Plastic Total", "PPE Total", "Metal Total", "Glass/Rubber Total",
                        "Paper/Cloth Total", "Fishing Debris Total", 
                        "Microplastics, Fibers, Fragments Total", "Foam Total", "Other Total"
                    ]
                    new_row["Total Total"] = sum(new_row[t] for t in totals_to_sum)

                    # 5. Save to CSV
                    new_df = pd.DataFrame([new_row])
                    updated_df = pd.concat([current_df, new_df], ignore_index=True)
                    updated_df.to_csv(DB_FILE, index=False)
                    
                    st.success(f"Log Entry Committed! Total Debris: {new_row['Total Total']}")
                    st.rerun()

# --- SECTION 2: HISTORY ---
    elif page == "History":
        st.title("CLEANUP DATA ARCHIVE")
        hist_df = df.copy()
        # Sort by date (latest first)
        hist_df = hist_df.sort_values(by='Date', ascending=False)

        # FORMAT THE DATE FOR DISPLAY ONLY
        hist_df['Date'] = hist_df['Date'].dt.strftime('%Y-%m-%d')
        
        search_q = st.text_input("SEARCH BY GEOGRAPHIC LOCATION", "")
        if search_q:
            # Search across Location, City, and Notes
            hist_df = hist_df[
                hist_df['Location'].astype(str).str.contains(search_q, case=False, na=False) | 
                hist_df['City'].astype(str).str.contains(search_q, case=False, na=False) |
                hist_df['Notes/comments'].astype(str).str.contains(search_q, case=False, na=False)
            ]

        st.markdown(f"**RECORD COUNT:** {len(hist_df)}")
        st.dataframe(hist_df, use_container_width=True)
        
        # Download button remains the same
        st.download_button(
            label="EXPORT ARCHIVE (CSV)", 
            data=hist_df.to_csv(index=False), 
            file_name="rozalia_master_archive.csv", 
            mime="text/csv"
        )

# --- SECTION 3: DASHBOARD ---
    elif page == "Dashboard":
        st.title("DATA DASHBOARD")

        # Prep DataFrame for filtering
        f_df = df.copy()
        f_df['Date_Converted'] = pd.to_datetime(f_df['Date'], errors='coerce')
        f_df['Year'] = f_df['Date_Converted'].dt.year.fillna("Unknown").astype(str)
        f_df['Month'] = f_df['Date_Converted'].dt.strftime('%B').fillna("Unknown")

        # --- STEP 1: FILTER DATA (Full Width Grid) ---
        st.markdown("### DATA CONTROLS")
        st.markdown("**STEP 1: FILTER DATA**")
        
        # 4-column grid for filters
        r1_c1, r1_c2, r1_c3, r1_c4 = st.columns(4)
        r2_c1, r2_c2, r2_c3, r2_c4 = st.columns(4)
        r3_c1, r3_c2, r3_c3, r3_c4 = st.columns(4)

        # Full original filter list
        filter_mapping = [
            ("Year", "Year", r1_c1), ("Month", "Month", r1_c2), 
            ("State", "State", r1_c3), ("City", "City", r1_c4),
            ("Type of cleanup", "Type of cleanup", r2_c1), ("Type of location", "Type of location", r2_c2),
            ("Recent events", "Recent events (human)", r2_c3), ("Weather", "Weather", r2_c4),
            ("Tide", "State of Tide", r3_c1), ("Flow", "Flow", r3_c2), 
            ("Recent weather", "Recent weather", r3_c3)
        ]

        for label, col_name, slot in filter_mapping:
            if col_name in f_df.columns:
                options = sorted(f_df[col_name].unique().astype(str))
                selected = slot.multiselect(f"SELECT {label.upper()}", options=options)
                if selected:
                    f_df = f_df[f_df[col_name].astype(str).isin(selected)]

        # --- STEP 2: VIEW DIMENSIONS (Stacked Below) ---
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("**STEP 2: VIEW DIMENSIONS**")
        group_options = ["Year", "State", "Type of cleanup", "Type of location", "Weather"]
        selected_groups = st.multiselect("GROUP DATA BY:", options=group_options, default=["Year"])

        # Record Count Display
        st.markdown(f"""
            <div style="padding: 10px 0px; color: #002b36; font-family: 'Avenir', sans-serif; margin-bottom: 50px;">
                <span style="font-size: 1.2rem; font-weight: 600; letter-spacing: 0.5px; text-transform: uppercase;">
                    {len(f_df):,} RECORDS MATCH YOUR FILTERS
                </span>
            </div>
        """, unsafe_allow_html=True)

        if f_df.empty or not selected_groups:
            st.warning("No data matches the selected filters or no Grouping selected.")
        else:
            # --- METRICS ---
            m1, m2, m3 = st.columns(3)
            total_p = int(f_df[ALL_DEBRIS_ITEMS].sum().sum())
            m1.metric("EXPEDITIONS", len(f_df))
            m2.metric("TOTAL PIECES", f"{total_p:,}")
            m3.metric("AVG PIECES", int(total_p / len(f_df)) if len(f_df) > 0 else 0)

            st.markdown("<br>", unsafe_allow_html=True)

            # --- TABS ---
            tab_main, tab_sub = st.tabs(["TOTAL COLLECTIONS", "SUBCATEGORY BREAKDOWNS"])

            with tab_main:
                st.subheader("MATERIAL TYPE")
                summary_list = []
                for cat, items in DEBRIS_GROUPS.items():
                    temp = f_df.groupby(selected_groups)[items].sum().sum(axis=1).reset_index(name="Count")
                    temp['Material'] = cat
                    summary_list.append(temp)
                
                plot_df = pd.concat(summary_list, ignore_index=True)
                
                if plot_df['Count'].sum() > 0:
                    plot_df['X_Axis'] = plot_df[selected_groups].astype(str).agg(' | '.join, axis=1)
                    
                    fig_stack = px.bar(
                        plot_df, x='X_Axis', y='Count', color='Material',
                        template="simple_white",
                        color_discrete_sequence=ROZALIA_PALETTE,
                        barmode='stack'
                    )
                    
                    fig_stack.update_layout(
                        barnorm='percent',
                        font_family="Avenir", 
                        yaxis_title="PROPORTION (%)", 
                        xaxis_title=None,
                        xaxis={'type': 'category'}
                    )
                    
                    fig_stack.update_traces(
                        hovertemplate="<b>%{fullData.name}</b><br>Total: %{customdata[0]:,} pieces<br>Share: %{y:.1f}%<extra></extra>",
                        customdata=plot_df[['Count']]
                    )
                    st.plotly_chart(fig_stack, use_container_width=True)
                else:
                    st.info("No debris data recorded for the current selection.")

            with tab_sub:
                st.subheader("SUBCATEGORY BREAKDOWNS")
                target_cat = st.selectbox("CHOOSE A SUBCATEGORY:", options=list(DEBRIS_GROUPS.keys()))
                
                sub_items = DEBRIS_GROUPS[target_cat]
                if f_df[sub_items].sum().sum() == 0:
                    st.warning(f"No {target_cat} items found for this selection.")
                else:
                    sub_plot_data = []
                    for item in sub_items:
                        temp = f_df.groupby(selected_groups)[item].sum().reset_index(name="Count")
                        temp['Item'] = item
                        sub_plot_data.append(temp)
                    
                    drill_df = pd.concat(sub_plot_data, ignore_index=True)
                    drill_df['X_Axis'] = drill_df[selected_groups].astype(str).agg(' | '.join, axis=1)

                    chart_type = st.radio("CHART TYPE:", ["Stacked Bar", "Pie Chart"], horizontal=True)

                    if chart_type == "Pie Chart":
                        pie_data = drill_df.groupby('Item')['Count'].sum().reset_index()
                        fig_sub = px.pie(pie_data, values='Count', names='Item',
                                         hole=0.4, color_discrete_sequence=ROZALIA_PALETTE)
                    else:
                        fig_sub = px.bar(drill_df, x='X_Axis', y='Count', color='Item',
                                         template="simple_white", color_discrete_sequence=ROZALIA_PALETTE)
                        fig_sub.update_layout(barnorm='percent', barmode='stack', yaxis_title="PROPORTION (%)", xaxis={'type': 'category'})
                    
                    fig_sub.update_layout(font_family="Avenir")
                    fig_sub.update_traces(
                        hovertemplate="<b>%{fullData.name}</b><br>Total: %{customdata[0]:,} pieces<br>Share: %{y:.1f}%<extra></extra>",
                        customdata=plot_df[['Count']]
                    )
                    st.plotly_chart(fig_sub, use_container_width=True)