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
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("TOTAL EXPEDITIONS", len(df))
        with col2:
            total_p = int(df[ALL_DEBRIS_ITEMS].sum().sum())
            st.metric("TOTAL DEBRIS PIECES", f"{total_p:,}")

        st.markdown("---")
        st.subheader("DISTRIBUTION BY CATEGORY")
        cat_sums = {cat: df[items].sum().sum() for cat, items in DEBRIS_GROUPS.items()}
        cat_df = pd.DataFrame(list(cat_sums.items()), columns=['Category', 'Count']).sort_values(by='Count', ascending=False)
        
        # Ocean-toned Bar Chart
        fig = px.bar(cat_df, x='Category', y='Count', 
                     template="simple_white",
                     color_discrete_sequence=['#004d4d'])
        fig.update_layout(font_family="Courier New", plot_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig, use_container_width=True)

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