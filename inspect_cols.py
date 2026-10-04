import pandas as pd
excel_path = "SentinelMCP_Dataset_Clean.xlsx"
xl = pd.ExcelFile(excel_path)
for s in ["Attack Workflows", "Benign Workflows"]:
    df = pd.read_excel(excel_path, sheet_name=s)
    print(f"\nSheet {s} Columns:", list(df.columns))
    print("First Row sample:", df.iloc[0].to_dict())
