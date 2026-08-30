"""
Find benign and targeted attack sessions in Traces - Main
"""
import pandas as pd

df = pd.read_excel('SentinelMCP_Dataset_Clean.xlsx', sheet_name='Traces - Main')
print("=== Labels Breakdown ===")
print(df['Label'].value_counts())

print("\n=== Attack Categories Breakdown ===")
print(df['Attack Category'].value_counts())

print("\n=== Benign Sample Sessions ===")
benign_df = df[df['Label'] == 'BENIGN']
for idx, r in benign_df.head(6).iterrows():
    print(f"ID: {r['Session ID']} | Prompt: '{r['User Prompt']}'")

print("\n=== Targeted Attack Sessions ===")
target_cats = [
    "POISONED_GITHUB_ISSUE",
    "CROSS_TOOL_PRIVILEGE_ESCALATION",
    "PRIVILEGE_ESCALATION",
    "CONTEXT_MANIPULATION",
    "UNAUTHORIZED_ACCESS",
    "TOOL_POISONING"
]

for cat in target_cats:
    matches = df[df['Attack Category'].astype(str).str.contains(cat, case=False, na=False)]
    if not matches.empty:
        r = matches.iloc[0]
        print(f"Cat: {r['Attack Category']} | ID: {r['Session ID']} | Prompt: '{r['User Prompt']}'")
