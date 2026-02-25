import pandas as pd
import os

# 1. SETUP - Make sure this matches the actual file on your Desktop/Folder
# If your file is named something else, change it here!
excel_file = "DataCSV2-25.csv" 
target_csv = "master_data.csv"

def run_migration():
    if not os.path.exists(excel_file):
        print(f"Error: Could not find '{excel_file}' in this folder.")
        print(f"Files currently in this folder: {os.listdir('.')}")
        return

    print("Reading Excel file... this might take 10-20 seconds.")
    # Reading the first sheet by default
    df = pd.read_csv(excel_file)

    # 2. DATE CLEANING
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    df['Year'] = df['Date'].dt.year
    df['Month'] = df['Date'].dt.strftime('%B')

    # 3. METADATA LOGIC
    categorical_cols = [
        'Location', 'City', 'State', 'Type of cleanup', 'Type of location', 
        'Weather', 'Weather (wind knots)', 'Recent weather', 'Tide', 'Flow', 
        'Recent events', 'Unusual items', 'Notes/comments'
    ]
    
    for col in categorical_cols:
        df[col] = df[col].astype(str).str.strip().str.title()

    df[categorical_cols] = df[categorical_cols].replace(['Nan', 'None', ''], 'Unknown')

    df['Outlier'] = df['Outlier'].fillna("").replace(['nan', 'None', 'Unknown'], "")

    # 4. NUMERIC LOGIC 

    numeric_cols = [
        'Distance cleaned (miles)', 
        'Duration (hrs)', 
        'Total weight (lb)', 
        '# of participants', 
    ]
    
    for col in numeric_cols:
            if col in df.columns:
                # Step A: Remove any non-numeric characters (like "lbs" or "miles")
                # This regex keeps digits and decimals, removes everything else
                df[col] = df[col].astype(str).str.replace(r'[^0-9.]', '', regex=True)
                
                # Step B: Convert to actual numbers
                df[col] = pd.to_numeric(df[col], errors='coerce')

    df = df.drop_duplicates() #in case the same cleanup gets submitted twice 

    # 5. SAVE TO CSV
    df.to_csv(target_csv, index=False, encoding='utf-8-sig')
    print(f"\nSuccess! '{target_csv}' created.")
    print(f"Rows processed: {len(df)}")

if __name__ == "__main__":
    run_migration()