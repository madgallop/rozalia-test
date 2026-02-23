import streamlit as st
import pandas as pd
import os
import plotly.express as px
from datetime import datetime, date
from config import DEBRIS_GROUPS, METADATA_FIELDS, DROPDOWN_OPTIONS

# --- SYSTEM CONFIGURATION ---
DB_FILE = "master_data.csv"
ALL_DEBRIS_ITEMS = [item for sublist in DEBRIS_GROUPS.values() for item in sublist]

def load_and_sync_data():
    """Load master dataset and align with configuration schema."""
    if not os.path.exists(DB_FILE):
        return pd.DataFrame()
    
    df = pd.read_csv(DB_FILE, low_memory=False)
    
    # Define structural order excluding Year/Month for the interface
    MASTER_ORDER = METADATA_FIELDS + ALL_DEBRIS_ITEMS
    for col in MASTER_ORDER:
        if col not in df.columns:
            df[col] = 0
            
    return df

# --- UI STYLING: ARCHIVAL OCEAN THEME ---
st.set_page_config(page_title="Rozalia Archive", layout="wide")

st.markdown("""
    <style>
        /* Scientific Archive Aesthetics */
        .main { background-color: #f4f1ea; } /* Aged paper color */
        h1, h2, h3 { font-family: 'Courier New', Courier, monospace; color: #002b36; }
        .stButton>button { 
            background-color: #002b36; 
            color: white; 
            border-radius: 0px;
            border: 1px solid #000;
        }
        .stDataFrame { border: 1px solid #002b36; }
        /* Sidebar styling */
        [data-testid="stSidebar"] { background-color: #e0d9c5; border-right: 1px solid #002b36; }
    </style>
""", unsafe_allow_html=True)

# Data Refresh
st.cache_data.clear()
df = load_and_sync_data()

if df.empty:
    st.error("Critical Error: Master Database File Missing or Corrupted.")
else:
    # --- NAVIGATION ---
    st.sidebar.title("ROZALIA PROJECT")
    st.sidebar.markdown("---")
    page = st.sidebar.radio("ARCHIVE SECTIONS", ["Dashboard", "New Entry", "History"])

# --- SECTION: DASHBOARD ---
    if page == "Dashboard":
        st.title("CLEANUP ANALYTICS")

        # --- SIDEBAR FILTERS ---
        st.sidebar.markdown("---")
        st.sidebar.subheader("ARCHIVE FILTERS")
        
        filter_df = df.copy()
        # On-the-fly date processing for filtering
        filter_df['Date_Converted'] = pd.to_datetime(filter_df['Date'], errors='coerce')
        filter_df['Year_Val'] = filter_df['Date_Converted'].dt.year.fillna("Unknown")

        # 1. Year Filter
        years = sorted(filter_df['Year_Val'].unique(), reverse=True)
        sel_year = st.sidebar.multiselect("SELECT YEAR(S)", options=years, default=years)

        # 2. State Filter (Replacing Location)
        states = sorted([str(x) for x in filter_df['State'].unique() if pd.notna(x)])
        sel_state = st.sidebar.multiselect("SELECT STATE(S)", options=states)

        # Apply logic
        mask = filter_df['Year_Val'].isin(sel_year)
        if sel_state:
            mask = mask & filter_df['State'].isin(sel_state)
        view_df = filter_df[mask]

        # --- KEY METRICS ---
        m1, m2, m3 = st.columns(3)
        total_p = int(view_df[ALL_DEBRIS_ITEMS].sum().sum())
        m1.metric("EXPEDITIONS", len(view_df))
        m2.metric("TOTAL PIECES", f"{total_p:,}")
        m3.metric("AVG PER CLEANUP", int(total_p / len(view_df)) if len(view_df) > 0 else 0)

        st.markdown("---")

        # --- SECTION 1: TOTAL PIECES FOUND (SORTABLE) ---
        st.subheader("TOTAL PIECES FOUND BY ITEM")
        
        item_counts = view_df[ALL_DEBRIS_ITEMS].sum().reset_index()
        item_counts.columns = ['Item', 'Count']

        sort_order = st.radio("SORT BY:", ["Frequency (Highest First)", "Item Name (A-Z)"], horizontal=True)
        
        if "Frequency" in sort_order:
            item_counts = item_counts.sort_values(by='Count', ascending=False)
        else:
            item_counts = item_counts.sort_values(by='Item')

        fig_items = px.bar(item_counts, x='Item', y='Count',
                           template="simple_white",
                           color_discrete_sequence=['#004d4d'])
        fig_items.update_layout(font_family="Courier New", height=500, plot_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig_items, use_container_width=True)

        st.markdown("---")

        # --- SECTION 2: MATERIAL BREAKDOWNS ---
        st.subheader("MATERIAL COMPOSITION")
        
        # 1. High-Level Overview Pie
        cat_sums = {cat: view_df[items].sum().sum() for cat, items in DEBRIS_GROUPS.items()}
        overall_pie_df = pd.DataFrame(list(cat_sums.items()), columns=['Category', 'Count'])
        
        fig_overall = px.pie(overall_pie_df, values='Count', names='Category', 
                             title="OVERALL CATEGORY DISTRIBUTION",
                             hole=0.4,
                             color_discrete_sequence=px.colors.sequential.Tealgrn)
        fig_overall.update_layout(font_family="Courier New")
        st.plotly_chart(fig_overall, use_container_width=True)

        st.markdown("---")
        st.subheader("DETAILED CATEGORY BREAKDOWNS")
        
        # 2. Automated Loop for All Categories
        # This creates a 2-column grid and makes a pie chart for every group in your config
        group_names = list(DEBRIS_GROUPS.keys())
        for i in range(0, len(group_names), 2):
            cols = st.columns(2)
            for j in range(2):
                if i + j < len(group_names):
                    cat_name = group_names[i + j]
                    items = DEBRIS_GROUPS[cat_name]
                    
                    sub_df = view_df[items].sum().reset_index()
                    sub_df.columns = ['Item', 'Count']
                    
                    # Only show the chart if there is actually data for this category
                    if sub_df['Count'].sum() > 0:
                        fig_sub = px.pie(sub_df, values='Count', names='Item', 
                                         title=f"{cat_name.upper()} DETAIL",
                                         hole=0.3,
                                         color_discrete_sequence=px.colors.sequential.Mint if j==0 else px.colors.sequential.Teal)
                        fig_sub.update_layout(font_family="Courier New")
                        cols[j].plotly_chart(fig_sub, use_container_width=True)
                    else:
                        cols[j].info(f"No data recorded for {cat_name} in the selected filters.")




    # --- SECTION: NEW ENTRY ---
    elif page == "New Entry":
        st.title("DATA ACQUISITION FORM")
        
        with st.form("entry_form", clear_on_submit=True):
            st.subheader("METADATA")
            meta_in = {}
            cols = st.columns(3)
            for i, field in enumerate(METADATA_FIELDS):
                c = cols[i % 3]
                label = field.upper()
                
                if field in DROPDOWN_OPTIONS:
                    meta_in[field] = c.selectbox(label, options=DROPDOWN_OPTIONS[field], index=None)
                elif "Date" in field:
                    meta_in[field] = c.date_input(label, date.today())
                elif any(x in field for x in ["Latitude", "Longitude", "Total weight", "Distance", "Duration"]):
                    meta_in[field] = c.number_input(label, value=0.0)
                else:
                    meta_in[field] = c.text_input(label)

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
                if not meta_in["Location"] or not meta_in["City"]:
                    st.warning("Incomplete Data: Location and City fields are mandatory.")
                else:
                    current_df = load_and_sync_data()
                    
                    # Merge inputs and format date to archive standard
                    new_row = {**meta_in, **counts}
                    new_row["Date"] = meta_in["Date"].strftime("%Y-%m-%d 00:00:00")
                    
                    # Ensure Year and Month are not added to the new_row dictionary
                    
                    updated_df = pd.concat([current_df, pd.DataFrame([new_row])], ignore_index=True)
                    updated_df.to_csv(DB_FILE, index=False)
                    
                    st.success("Log Entry Committed Successfully.")
                    st.rerun()

    # --- SECTION: HISTORY ---
    elif page == "History":
        st.title("MASTER ARCHIVE RECORDS")
        
        # Load directly and exclude Year/Month from display
        hist_df = pd.read_csv(DB_FILE, low_memory=False)
        
        # Temporal Sorting
        hist_df['Sort_Date'] = pd.to_datetime(hist_df['Date'], errors='coerce')
        hist_df = hist_df.sort_values(by='Sort_Date', ascending=False)
        
        # Search Filter
        search_q = st.text_input("SEARCH BY GEOGRAPHIC LOCATION", "")
        if search_q:
            hist_df = hist_df[hist_df['Location'].astype(str).str.contains(search_q, case=False, na=False) | 
                              hist_df['City'].astype(str).str.contains(search_q, case=False, na=False)]

        # Filter out Year/Month and temporary sort column
        display_cols = [c for c in hist_df.columns if c not in ['Year', 'Month', 'Sort_Date']]
        final_display = hist_df[display_cols]
        
        st.markdown(f"**RECORD COUNT:** {len(final_display)}")
        st.dataframe(final_display, use_container_width=True)
        
        st.download_button(
            label="EXPORT ARCHIVE (CSV)",
            data=final_display.to_csv(index=False),
            file_name="rozalia_master_archive.csv",
            mime="text/csv"
        )