import pandas as pd
import os

# 1. SETUP - Make sure this matches the actual file on your Desktop/Folder
# If your file is named something else, change it here!
excel_file = "DataWithFoamForUpload.xlsx" 
target_csv = "master_data.csv"

def run_migration():
    if not os.path.exists(excel_file):
        print(f"Error: Could not find '{excel_file}' in this folder.")
        print(f"Files currently in this folder: {os.listdir('.')}")
        return

    print("Reading Excel file... this might take 10-20 seconds.")
    # Reading the first sheet by default
    df = pd.read_excel(excel_file)

    # 2. DATE CLEANING
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    df['Year'] = df['Date'].dt.year.fillna("Unknown")
    df['Month'] = df['Date'].dt.strftime('%B').fillna("Unknown")

    # 3. METADATA MAPPING (Matching your specific Excel headers)
    categorical_cols = [
        'Type of cleanup', 
        'Type of location', 
        'Weather', 
        'Recent weather', 
        'Tide', 
        'Flow', 
        'Recent events'
    ]
    
    for col in categorical_cols:
        if col in df.columns:
            df[col] = df[col].fillna("Unknown").astype(str).replace(["nan", ""], "Unknown")
        else:
            print(f"Warning: Column '{col}' not found in Excel!")

    # 4. NUMERIC MAPPING (Matching your specific Wind header)
    numeric_cols = [
        'Distance cleaned (miles)', 
        'Duration (hrs)', 
        'Wind (knots) 0 if none', 
        'Total weight (lb)', 
        '# of participants'
    ]
    
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

    # 5. SAVE TO CSV
    # We use encoding='utf-8-sig' to make sure it's readable by both Python and Excel
    df.to_csv(target_csv, index=False, encoding='utf-8-sig')
    print(f"\nSuccess! '{target_csv}' created.")
    print(f"Rows processed: {len(df)}")

if __name__ == "__main__":
    run_migration()