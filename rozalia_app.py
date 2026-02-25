#import essential libraries 
import streamlit as st
import pandas as pd
import os
import plotly.express as px
from datetime import datetime, date

# get info from config file
from config import DEBRIS_GROUPS, METADATA_FIELDS, SUMMARY_TOTALS, DROPDOWN_OPTIONS

# --- SYSTEM CONFIGURATION ---
DB_FILE = "master_data.csv"

ROZALIA_PALETTE = ["#7BB3CC", "#E8A85D", "#92AD94", "#A4C3B2", "#BC6C25", "#8D99AE", "#D4A373", "#788794", "#E9EDC9"]

ALL_DEBRIS_ITEMS = [item for sublist in DEBRIS_GROUPS.values() for item in sublist]


def load_and_sync_data():
    if not os.path.exists(DB_FILE):
        return pd.DataFrame()
    
    df = pd.read_csv(DB_FILE, low_memory=False)
    
    # 2. Drop unwanted columns
    cols_to_drop = ['Year', 'Month', 'Day']
    df.drop(columns=[c for c in cols_to_drop if c in df.columns], inplace=True)
    
    # 3. Ensure all metadata columns exist (default fill "Unknown" or 0). prevents crashing if new columns added in config.
    for col in METADATA_FIELDS:
        if col not in df.columns:
            if any(unit in col.lower() for unit in ['lb', 'miles', 'hrs', '#', 'knots']):
                df[col] = 0
            else:
                df[col] = "Unknown"

    # 4. Ensure all debris count columns exist (default fill to 0)
    for col in ALL_DEBRIS_ITEMS:
        if col not in df.columns:
            df[col] = 0
        else:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0) #needs to be 0 and not NaN for calculating totals 

    # 5. Ensure all summary total columns exist (default to 0)
    # This is where we use the new SUMMARY_TOTALS list from config
    for col in SUMMARY_TOTALS:
        if col not in df.columns:
            df[col] = 0
        else:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0) #needs to be 0 and not NaN for calculating totals 

    # 7. FINAL REORDERING
    existing_meta = [c for c in METADATA_FIELDS if c in df.columns] 
    existing_debris = [c for c in ALL_DEBRIS_ITEMS if c in df.columns]   
    existing_totals = [c for c in SUMMARY_TOTALS if c in df.columns]
    remaining = [c for c in df.columns if c not in existing_meta + existing_debris + existing_totals]

    new_column_order = existing_meta + existing_debris + existing_totals + remaining
    df = df[new_column_order]
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    return df

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
        with st.form("entry_form", clear_on_submit=True):
            st.subheader("METADATA")
            meta_in = {}
            cols = st.columns(3)

            # Define which fields are mandatory
            REQUIRED_FIELDS = ["Date", "Location", "City", "State"]

            for i, field in enumerate(METADATA_FIELDS):
                if field == "Outlier": continue 
                
                c = cols[i % 3]
                
                # Create the label: Uppercase it and add a red star if required
                display_label = field.upper().replace("#", "NUMBER")
                if field in REQUIRED_FIELDS:
                    display_label = f"{display_label} :red[*]"

                if field in DROPDOWN_OPTIONS:
                    meta_in[field] = c.selectbox(display_label, options=DROPDOWN_OPTIONS[field], index=None)
                
                elif "Date" in field:
                    meta_in[field] = c.date_input(display_label, date.today())
                    
                elif any(x in field for x in ["Total weight", "Distance", "Duration"]):
                    # Floats for weights/miles
                    meta_in[field] = c.number_input(display_label, min_value=0.0, step=0.1, value=0.0)
                    
                elif "Participants" in field or "#" in field:
                    # Integers for people
                    meta_in[field] = c.number_input(display_label, min_value=0, step=1, value=0)
                    
                else:
                    meta_in[field] = c.text_input(display_label)

            st.markdown("---")
            st.subheader("DEBRIS QUANTIFICATION")
            counts = {}
            tabs = st.tabs([k.upper() for k in DEBRIS_GROUPS.keys()])
            for i, (group_name, items) in enumerate(DEBRIS_GROUPS.items()):
                with tabs[i]:
                    d_cols = st.columns(3)
                    for j, item in enumerate(items):
                        counts[item] = d_cols[j % 3].number_input(item, min_value=0, step=1)

            if st.form_submit_button("COMMIT TO MASTER LOG"):
                missing_fields = [r for r in REQUIRED_FIELDS if not meta_in.get(r)]
                
                if missing_fields:
                    st.error(f"Missing required fields: {', '.join(missing_fields)}")
                else:
                    # 2. PREPARE ROW & UNIFY DATE KEY
                    new_row = {**meta_in, **counts}
                    new_row["Date"] = pd.to_datetime(meta_in["Date"])
                    
                    # 3. AUTO-CALCULATE ALL TOTALS 
                    category_to_total_col = {
                        "Plastic": "Total Plastic",
                        "Foam": "Total Foam",
                        "PPE": "Total PPE",
                        "Metal": "Total Metal",
                        "Glass & Rubber": "Total Glass & Rubber",
                        "Paper & Cloth": "Total Paper & Cloth",
                        "Fishing Debris": "Total Fishing Debris",
                        "Microplastics & Fibers": "Total Microplastics"
                    }

                    grand_total = 0
                    for group_name, total_col in category_to_total_col.items():
                        group_sum = sum(counts.get(item, 0) for item in DEBRIS_GROUPS.get(group_name, []))
                        new_row[total_col] = group_sum
                        grand_total += group_sum
                    
                    grand_total += sum(counts.get(item, 0) for item in DEBRIS_GROUPS.get("Other", []))
                    new_row["Grand Total"] = grand_total

                    # 4. LOAD, CONCAT, AND PROTECT COLUMNS
                    current_df = load_and_sync_data()
                    new_df = pd.DataFrame([new_row])
                    
                    updated_df = pd.concat([current_df, new_df], ignore_index=True)
                    
                    # FILTER: Only save columns that exist in your config
                    allowed = METADATA_FIELDS + ALL_DEBRIS_ITEMS + SUMMARY_TOTALS + ["Date"]
                    final_cols = [c for c in updated_df.columns if c in allowed]
                    # Remove exact duplicates in final_cols list while keeping order
                    final_cols = list(dict.fromkeys(final_cols))
                    
                    updated_df = updated_df[final_cols]
                    
                    # 5. SAVE
                    updated_df.to_csv(DB_FILE, index=False, encoding='utf-8-sig')
                    st.cache_data.clear() # Refresh history immediately
                    st.success(f"Entry Saved! Grand Total: {grand_total}")
                    st.balloons()
                    st.rerun()
            

# --- SECTION 2: HISTORY ---
    elif page == "History":
        st.title("CLEANUP DATA ARCHIVE")
        hist_df = load_and_sync_data()
        
        if not hist_df.empty:
            # 1. Clean up Date column before sorting
            hist_df['Date'] = pd.to_datetime(hist_df['Date'], errors='coerce')
            hist_df = hist_df.sort_values(by='Date', ascending=False)

            # 2. Search Logic
            search_q = st.text_input("SEARCH BY LOCATION, CITY, OR NOTES", "").strip()
            if search_q:
                mask = (
                    hist_df['Location'].astype(str).str.contains(search_q, case=False, na=False) | 
                    hist_df['City'].astype(str).str.contains(search_q, case=False, na=False)
                )
                hist_df = hist_df[mask]

            # 3. Format Date for DISPLAY ONLY
            display_df = hist_df.copy()
            # This turns '2024-02-25 00:00:00' into '2024-02-25'
            # If date is missing, it shows "Missing Date" instead of None
            display_df['Date'] = display_df['Date'].dt.strftime('%Y-%m-%d').fillna("Missing Date")

            st.markdown(f"**RECORD COUNT:** {len(display_df)}")
            st.dataframe(display_df, use_container_width=True)
            
            # Download
            st.download_button(
                label="EXPORT CSV", 
                data=hist_df.to_csv(index=False).encode('utf-8-sig'), 
                file_name="cleanup_archive.csv", 
                mime="text/csv"
            )




# --- SECTION 3: DASHBOARD ---
    elif page == "Dashboard":
        st.title("DATA DASHBOARD")

        # 1. Efficient Data Preparation
        f_df = df.copy()
        f_df['Date'] = pd.to_datetime(f_df['Date'], errors='coerce')
        f_df['Year'] = f_df['Date'].dt.year.fillna("Unknown").astype(str)
        f_df['Month'] = f_df['Date'].dt.month_name().fillna("Unknown")

        # --- STEP 0: TOP DATA CHARTS ---
        with st.expander("CONFIGURE TOP DATA CHARTS", expanded=True):

            t_col1, t_col2, t_col3 = st.columns([2, 2, 1])
            
            # DEFAULT: Total Pieces (Count)
            sort_method = t_col1.radio(
                "SELECT VIEW:", 
                ["Total Pieces (Count)", "Frequency (%)"],
                index=0,  # Sets 'Total Pieces' as default
                help="Total Pieces: Sum of all items found. Frequency: % of cleanups where item was found."
            )
            
            # DEFAULT: Toggle ON
            group_sizes = t_col2.toggle("Group Sizes (Micro/Small/Large)", value=True)
            num_bars = t_col3.number_input("Number of Bars:", min_value=3, max_value=25, value=10)

            # 1. Prep Data
            top_df_raw = df.copy()
            total_cleanups = len(top_df_raw)
            
            # 2. Define sub-groups matching your Tier naming exactly
            size_groups = {
                "Grouped Microplastics": ["Micro plastic 0-5mm", "SMALL plastic 5-30mm", "LARGE plastic >30mm"],
                "Grouped Microfoams": ["Micro foam 0-5mm", "SMALL foam 5-30mm", "LARGE foam >30mm"],
                "Grouped Microfibers": ["Line/net fiber: MICRO 0-5mm", "Line/net fiber: SMALL 5-30mm", "Line/net fiber: LARGE >30mm"]
            }

            plot_items = ALL_DEBRIS_ITEMS.copy()

            if group_sizes:
                for group_name, items in size_groups.items():
                    valid_items = [i for i in items if i in top_df_raw.columns]
                    if valid_items:
                        top_df_raw[group_name] = top_df_raw[valid_items].sum(axis=1)
                        plot_items = [i for i in plot_items if i not in valid_items]
                        plot_items.append(group_name)

            # 3. Calculation Logic
            if not top_df_raw.empty:
                if "Frequency" in sort_method:
                    counts = (top_df_raw[plot_items] > 0).sum().reset_index()
                    counts.columns = ['Item', 'Cleanups_Found']
                    counts['Value'] = (counts['Cleanups_Found'] / total_cleanups) * 100
                    y_label = "PERCENT OF EXPEDITIONS (%)"
                    suffix = "%"
                    text_fmt = '.1f'
                else:
                    counts = top_df_raw[plot_items].sum().reset_index()
                    counts.columns = ['Item', 'Value']
                    counts['Cleanups_Found'] = (top_df_raw[plot_items] > 0).sum().values
                    y_label = "TOTAL PIECES COLLECTED"
                    suffix = " pieces"
                    text_fmt = ','

                # 4. Filter, Sort, and Build Chart
                top_plot_df = counts.sort_values(by='Value', ascending=False).head(num_bars)

                fig_top = px.bar(
                    top_plot_df, x='Item', y='Value',
                    template="simple_white",
                    color_discrete_sequence=[ROZALIA_PALETTE[3]], 
                    text_auto=text_fmt
                )

                fig_top.update_traces(
                    hovertemplate=(
                        "<b>%{x}</b><br>" +
                        f"{'Frequency' if 'Frequency' in sort_method else 'Total'}: %{{y:.1f}}{suffix}<br>" +
                        "Found in %{customdata[0]} expeditions<extra></extra>"
                    ),
                    customdata=top_plot_df[['Cleanups_Found']]
                )

                fig_top.update_layout(
                    title=f"Top {num_bars} Items Found: {sort_method}",
                    xaxis_title=None,
                    yaxis_title=y_label,
                    font_family="Avenir",
                    xaxis={'categoryorder':'total descending'}
                )
                st.plotly_chart(fig_top, use_container_width=True)


        # --- STEP 1: FILTER DATA ---
        st.markdown("### DATA CONTROLS")
        filter_cols = ["Year", "Month", "State", "City", "Type of cleanup", "Type of location", "Weather", "Tide"]
        
        # Grid layout for filters
        rows = [filter_cols[i:i + 4] for i in range(0, len(filter_cols), 4)]
        for row in rows:
            cols = st.columns(4)
            for idx, col_name in enumerate(row):
                if col_name in f_df.columns:
                    options = sorted(f_df[col_name].unique().astype(str))
                    selected = cols[idx].multiselect(f"SELECT {col_name.upper()}", options=options)
                    if selected:
                        f_df = f_df[f_df[col_name].astype(str).isin(selected)]

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
            m1.metric("EXPEDITIONS", f"{len(f_df):,}")
            m2.metric("TOTAL PIECES", f"{total_pieces:,}")
            m3.metric("AVG PIECES", f"{int(total_pieces / len(f_df)) if len(f_df) > 0 else 0:,}")

            tab_main, tab_sub = st.tabs(["TOTAL COLLECTIONS", "SUBCATEGORY BREAKDOWNS"])

            with tab_main:
                st.subheader("MATERIAL TYPE")
                cat_data = []
                for cat, items in DEBRIS_GROUPS.items():
                    cat_sum = f_df.groupby('X_Axis')[items].sum().sum(axis=1).reset_index(name='Count')
                    cat_sum['Material'] = cat
                    cat_data.append(cat_sum)
                
                plot_df = pd.concat(cat_data)

                fig_stack = px.bar(
                    plot_df, x='X_Axis', y='Count', color='Material',
                    template="simple_white",
                    color_discrete_sequence=ROZALIA_PALETTE,
                    barmode='stack',
                    category_orders={"X_Axis": sorted(plot_df['X_Axis'].unique())}
                )
                
                # REVERTED: Using your specific hovertemplate logic
                fig_stack.update_traces(
                    hovertemplate="<b>%{fullData.name}</b><br>Total: %{customdata[0]:,} pieces<br>Share: %{y:.1f}%<extra></extra>",
                    customdata=plot_df[['Count']]
                )

                fig_stack.update_layout(
                    barnorm='percent', 
                    yaxis_title="PROPORTION (%)", 
                    xaxis_title=None,
                    font_family="Avenir"
                )
                st.plotly_chart(fig_stack, use_container_width=True)

            with tab_sub:
                st.subheader("SUBCATEGORY BREAKDOWNS")
                target_cat = st.selectbox("CHOOSE A SUBCATEGORY:", options=list(DEBRIS_GROUPS.keys()))
                sub_items = DEBRIS_GROUPS[target_cat]
                
                # Filter out items with 0 counts to keep the chart clean
                item_counts = f_df[sub_items].sum()
                active_items = item_counts[item_counts > 0].index.tolist()

                if not active_items:
                    st.info(f"No {target_cat} items found for this selection.")
                else:
                    sub_df = f_df.melt(id_vars=['X_Axis'], value_vars=active_items, var_name='Item', value_name='Count')
                    sub_df = sub_df.groupby(['X_Axis', 'Item'])['Count'].sum().reset_index()

                    chart_type = st.radio("VIEW AS:", ["Stacked Bar", "Pie Chart"], horizontal=True)

                    if chart_type == "Pie Chart":
                        fig_sub = px.pie(sub_df, values='Count', names='Item', hole=0.4,
                                         color_discrete_sequence=ROZALIA_PALETTE)
                        fig_sub.update_traces(
                            hovertemplate="<b>%{label}</b><br>Total: %{value:,} pieces<extra></extra>"
                        )
                    else:
                        fig_sub = px.bar(sub_df, x='X_Axis', y='Count', color='Item',
                                         template="simple_white", color_discrete_sequence=ROZALIA_PALETTE,
                                         category_orders={"X_Axis": sorted(sub_df['X_Axis'].unique())})
                        fig_sub.update_layout(barnorm='percent', yaxis_title="PROPORTION (%)")
                        fig_sub.update_traces(
                            hovertemplate="<b>%{fullData.name}</b><br>Total: %{customdata[0]:,} pieces<br>Share: %{y:.1f}%<extra></extra>",
                            customdata=sub_df[['Count']] 
                        )
                    

            
                    
                    fig_sub.update_layout(xaxis_title=None, font_family="Avenir")
                    st.plotly_chart(fig_sub, use_container_width=True)