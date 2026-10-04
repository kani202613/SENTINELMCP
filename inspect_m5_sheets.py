import pandas as pd
import json

excel_path = "SentinelMCP_Dataset_Clean.xlsx"
xl = pd.ExcelFile(excel_path)
print("Sheet Names:", xl.sheet_names)

for sheet in ["Attack Workflows", "Benign Workflows"]:
    if sheet in xl.sheet_names:
        df = pd.read_excel(excel_path, sheet_name=sheet)
        print(f"\n--- {sheet} ({len(df)} rows) ---")
        print("Columns:", list(df.columns))
        for idx, r in df.iterrows():
            print(f"\nRow {idx+1}: Workflow ID={r.get('Workflow ID', r.get('ID'))} | Category={r.get('Workflow Name', r.get('Category'))}")
            print("Prompt:", str(r.get('Initial User Prompt', r.get('User Prompt')))[:100])
            raw = str(r.get('Trace Steps', r.get('Raw Trace Details', '')))
            try:
                steps = json.loads(raw)
                print(f"Steps count: {len(steps)}")
            except Exception as e:
                print("Steps parse error:", e)
