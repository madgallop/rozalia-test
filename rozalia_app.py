import streamlit as st
import pandas as pd
import os
import plotly.express as px
from datetime import datetime, date
from config import DEBRIS_GROUPS, METADATA_FIELDS, DROPDOWN_OPTIONS

# --- SYSTEM CONFIGURATION ---
DB_FILE = "master_data.csv"
ALL_DEBRIS_ITEMS = [item for sublist in DEBRIS_GROUPS.values() for item in sublist]
ROZALIA_PALETTE = [
    "#59AEBE", # Plastic: Lighter, cleaner Slate Blue
    "#C78D0D", # Wood: Warm Amber
    "#A1B5E2", # Fishing Gear: Deep Moss Green
    "#757560", # Glass: Light Mint/Aqua (distinct from blue/green)
    "#48733D", # Rubber: Strong Terracotta (warm contrast)
    "#755268", # Metal: Neutral Pebble Grey
    "#E6BAF2", # Bio-debris: Toasted Sand
    "#F2F2BB", # Cloth/Fabric: Navy Slate
    "#C6F2BB"  # Other: Pale Sage (very light neutral)
]
def load_and_sync_data():
    """Load master dataset and align with configuration schema."""
    if not os.path.exists(DB_FILE):
        return pd.DataFrame()
    
    df = pd.read_csv(DB_FILE, low_memory=False)
    
    MASTER_ORDER = METADATA_FIELDS + ALL_DEBRIS_ITEMS
    for col in MASTER_ORDER:
        if col not in df.columns:
            df[col] = 0
            
    return df

# --- UI STYLING: ARCHIVAL OCEAN THEME ---
st.set_page_config(page_title="Rozalia Archive", layout="wide")

# st.markdown("""
#     <style>
#         .main { background-color: #f4f1ea; }
#         h1, h2, h3 { font-family: 'Avenir New', Avenir, monospace; color: #fffdfa; }
        
#         /* Highlighter Yellow Accents */
#         .stButton>button { 
#             background-color: #ffffb3; 
#             color: #002b36; 
#             border-radius: 0px;
#             border: 2px solid #002b36;
#             font-weight: bold;
#         }
#         # .stButton>button:hover { background-color: #f0f096; border: 2px solid #015369; }
        
#         /* Metric Styling */
#         [data-testid="stMetricValue"] { color: #002b36; background-color: #f4f1ea; padding: 5px; }
        
#         /* Sidebar Styling */
#         [data-testid="stSidebar"] { background-color: #f7f3e6; border-right: 1px solid #002b36; }
        
#         # /* Dataframe border */
#         # .stDataFrame { border: 1px solid #002b36; }
#     </style>
# """, unsafe_allow_html=True)

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

        # --- STEP 1: CASCADING FILTERS (Slicers) ---
        st.sidebar.markdown("### STEP 1: FILTER DATA")
        st.sidebar.caption("Optional: Hold Ctrl to select multiple. Filters are linked.")

        f_df = df.copy()
        f_df['Date_Converted'] = pd.to_datetime(f_df['Date'], errors='coerce')
        f_df['Year'] = f_df['Date_Converted'].dt.year.fillna("Unknown").astype(str)
        f_df['Month'] = f_df['Date_Converted'].dt.strftime('%B').fillna("Unknown")

        filter_cols = {
            "Year": "Year",
            "Month": "Month",
            "State": "State",
            "City": "City",
            "Type of cleanup": "Type of cleanup",
            "Type of location": "Type of location",
            "Recent events": "Recent events (human)",
            "Weather": "Weather",
            "Tide": "State of Tide",
            "Flow": "Flow",
            "Recent weather": "Recent weather"
        }

        active_filters = {}
        for label, col in filter_cols.items():
            if col in f_df.columns:
                available_options = sorted(f_df[col].unique().astype(str))
                selected = st.sidebar.multiselect(f"SELECT {label.upper()}", options=available_options)
                if selected:
                    f_df = f_df[f_df[col].astype(str).isin(selected)]
                    active_filters[col] = selected

        # --- STEP 2: GROUPING SELECTION ---
        st.markdown("### STEP 2: SELECT VIEW DIMENSIONS")
        group_options = ["Year", "State", "Type of cleanup", "Type of location", "Weather"]
        selected_groups = st.multiselect("GROUP DATA BY:", options=group_options, default=["Year"])

        st.markdown(
            f"""
            <div style="
                # background-color: #D1AE3B; 
                padding: 10px; 
                color: #1C396C; 
                font-family: 'Avenir', monospace;
                margin-bottom: 20;
            ">
                <strong>{len(f_df)} records match your filters.</strong>
            </div>
            """, 
            unsafe_allow_html=True
        )
        st.markdown("<br>", unsafe_allow_html=True)

        if f_df.empty or not selected_groups:
            st.warning("No data matches the selected filters or no Grouping selected.")
        else:
            # --- METRICS ---
            m1, m2, m3 = st.columns(3)
            total_p = int(f_df[ALL_DEBRIS_ITEMS].sum().sum())
            m1.metric("EXPEDITIONS", len(f_df))
            m2.metric("TOTAL PIECES", f"{total_p:,}")
            m3.metric("AVG PIECES", int(total_p / len(f_df)) if len(f_df) > 0 else 0)

            # --- TABS ---
            tab_main, tab_sub = st.tabs(["TOTAL COLLECTIONS", "SUBCATEGORY DRILL-DOWN"])

            with tab_main:
                st.subheader("PROPORTIONAL MATERIAL TYPE (0-100%)")
                
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
                        color_discrete_sequence=ROZALIA_PALETTE
                    )
                    
                    fig_stack.update_layout(
                        barmode='stack', barnorm='percent',
                        font_family="Avenir", 
                        yaxis_title="PROPORTION (%)", 
                        xaxis_title=" | ".join(selected_groups).upper(),
                        xaxis={'type': 'category'}
                    )
                    
                    fig_stack.update_traces(
                        hovertemplate="<b>%{fullData.name}</b><br>Total: %{customdata[0]} pieces<br>Share: %{y:.1f}%<extra></extra>",
                        customdata=plot_df[['Count']]
                    )
                    st.plotly_chart(fig_stack, use_container_width=True)
                else:
                    st.info("No debris data recorded for the current selection.")

            with tab_sub:
                st.subheader("SPECIFIC ITEM BREAKDOWNS")
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
                        fig_sub.update_traces(
                            textinfo='percent+label',
                            hovertemplate="<b>%{label}</b><br>Total: %{value} pieces<br>%{percent}<extra></extra>"
                        )
                    else:
                        fig_sub = px.bar(drill_df, x='X_Axis', y='Count', color='Item',
                                         template="simple_white", color_discrete_sequence=ROZALIA_PALETTE)
                        fig_sub.update_layout(barmode='stack', barnorm='percent', yaxis_title="PROPORTION (%)", xaxis={'type': 'category'})
                        fig_sub.update_traces(
                            hovertemplate="<b>%{fullData.name}</b><br>Total: %{customdata[0]} pieces<br>Share: %{y:.1f}%<extra></extra>",
                            customdata=drill_df[['Count']]
                        )
                    
                    fig_sub.update_layout(font_family="Avenir")
                    st.plotly_chart(fig_sub, use_container_width=True)

    # --- SECTION: NEW ENTRY ---
    elif page == "New Entry":
        st.title("DATA ACQUISITION FORM")
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

    # --- SECTION: HISTORY ---
    elif page == "History":
        st.title("MASTER ARCHIVE RECORDS")
        hist_df = pd.read_csv(DB_FILE, low_memory=False)
        hist_df['Sort_Date'] = pd.to_datetime(hist_df['Date'], errors='coerce')
        hist_df = hist_df.sort_values(by='Sort_Date', ascending=False)
        
        search_q = st.text_input("SEARCH BY GEOGRAPHIC LOCATION", "")
        if search_q:
            hist_df = hist_df[hist_df['Location'].astype(str).str.contains(search_q, case=False, na=False) | 
                              hist_df['City'].astype(str).str.contains(search_q, case=False, na=False)]

        display_cols = [c for c in hist_df.columns if c not in ['Year', 'Month', 'Sort_Date']]
        st.markdown(f"**RECORD COUNT:** {len(hist_df)}")
        st.dataframe(hist_df[display_cols], use_container_width=True)
        
        st.download_button(label="EXPORT ARCHIVE (CSV)", data=hist_df[display_cols].to_csv(index=False), file_name="rozalia_master_archive.csv", mime="text/csv")