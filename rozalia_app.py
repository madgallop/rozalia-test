import streamlit as st
import pandas as pd
import os
import plotly.express as px
from datetime import datetime, date
from config import DEBRIS_GROUPS, METADATA_FIELDS, DROPDOWN_OPTIONS

# --- SYSTEM CONFIGURATION ---
DB_FILE = "master_data.csv"
ALL_DEBRIS_ITEMS = [item for sublist in DEBRIS_GROUPS.values() for item in sublist]

# Your custom categorical palette
ROZALIA_PALETTE = [
    "#7BB3CC", # Plastic
    "#E8A85D", # Wood/Microplastics
    "#92AD94", # Fibers/Sage
    "#A4C3B2", # Glass
    "#BC6C25", # Rubber
    "#8D99AE", # Metal
    "#D4A373", # Bio-debris
    "#788794", # Cloth/Fabric (Toned down)
    "#E9EDC9"  # Other
]

def load_and_sync_data():
    """Load master dataset and align with configuration schema."""
    if not os.path.exists(DB_FILE):
        return pd.DataFrame()
    
    df = pd.read_csv(DB_FILE, low_memory=False)
    
    # 1. Standardize Dates
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    
    # 2. Fix the Categories (The "No Options" Fix)
    # These columns MUST be strings so the dropdowns can show them
    categorical_fields = [
        'Year', 'Month', 'State', 'City', 'Type of cleanup', 
        'Type of location', 'Weather', 'Recent weather', 
        'Tide', 'Flow', 'Recent events'
    ]
    
    for col in categorical_fields:
        if col in df.columns:
            # Replace empty/NaN with 'Unknown'
            df[col] = df[col].fillna("Unknown").astype(str).replace(["nan", ""], "Unknown")
        else:
            # If the column is missing entirely, create it
            df[col] = "Unknown"

    # 3. Fix the Numbers (Debris and Stats)
    # This ensures columns like "Total weight (lb)" don't break the charts
    numeric_fields = ALL_DEBRIS_ITEMS + [
        'Distance cleaned (miles)', 'Duration (hrs)', 
        'Wind (knots) 0 if none', 'Total weight (lb)', '# of participants'
    ]
    
    for col in numeric_fields:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        else:
            df[col] = 0
            
    return df

# --- UI STYLING ---
st.set_page_config(page_title="Rozalia Archive", layout="wide")

# Data Refresh
df = load_and_sync_data()

if df.empty:
    st.error("Critical Error: Master Database File Missing or Corrupted.")
else:
    # --- NAVIGATION ---
    st.sidebar.title("ROZALIA PROJECT")
    st.sidebar.markdown("---")
    # Default order: New Entry -> History -> Dashboard
    page = st.sidebar.radio("SECTIONS", ["New Entry", "History", "Dashboard"])

    # --- SECTION 1: NEW ENTRY (Default Landing Page) ---
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
                elif any(x in field for x in ["Latitude", "Longitude", "Total weight", "Distance", "Duration"]):
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
                    current_df = load_and_sync_data()
                    new_row = {**meta_in, **counts}
                    new_row["Date"] = meta_in["Date"].strftime("%Y-%m-%d 00:00:00")
                    updated_df = pd.concat([current_df, pd.DataFrame([new_row])], ignore_index=True)
                    updated_df.to_csv(DB_FILE, index=False)
                    st.success("Log Entry Committed Successfully.")
                    st.rerun()

    # --- SECTION 2: HISTORY ---
    elif page == "History":
        st.title("CLEANUP DATA ARCHIVE")
        hist_df = df.copy()
        hist_df['Sort_Date'] = pd.to_datetime(hist_df['Date'], errors='coerce')
        hist_df = hist_df.sort_values(by='Sort_Date', ascending=False)
        
        search_q = st.text_input("SEARCH BY GEOGRAPHIC LOCATION", "")
        if search_q:
            hist_df = hist_df[hist_df['Location'].astype(str).str.contains(search_q, case=False, na=False) | 
                              hist_df['City'].astype(str).str.contains(search_q, case=False, na=False)]

        display_cols = [c for c in hist_df.columns if c not in ['Sort_Date']]
        st.markdown(f"**RECORD COUNT:** {len(hist_df)}")
        st.dataframe(hist_df[display_cols], use_container_width=True)
        
        st.download_button(
            label="EXPORT ARCHIVE (CSV)", 
            data=hist_df[display_cols].to_csv(index=False), 
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
            ("Recent events", "Recent events", r2_c3), ("Weather", "Weather", r2_c4),
            ("Tide", "Tide", r3_c1), ("Flow", "Flow", r3_c2), 
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
                target_cat = st.selectbox("CHOOSE A CATEGORY TO DRILL DOWN:", options=list(DEBRIS_GROUPS.keys()))
                
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
                    st.plotly_chart(fig_sub, use_container_width=True)