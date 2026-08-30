import pandas as pd
import json

excel_path = "SentinelMCP_Dataset_Clean.xlsx"
df = pd.read_excel(excel_path, sheet_name="Traces - Set B (Red-Team)")
print("Columns:", list(df.columns))
print("Categories:", df['Attack Category'].unique())
for idx, r in df.iterrows():
    if str(r.get("Label")) == "ATTACK":
        print("ATTACK Session ID:", r["Session ID"], "| Category:", r.get("Attack Category"))
        steps = json.loads(str(r["Raw Trace Details"]))
        for s in steps:
            print("  Step:", s)
        break
