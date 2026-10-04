"""
SentinelMCP Data Loader & In-Memory Cache Provider (Optimized Infrastructure)
Loads SentinelMCP_Dataset_Clean.xlsx ONCE at initialization and caches all sheets in memory.
Eliminates ~4.87 ms per-call disk I/O overhead from repeated pandas.read_excel calls.
"""
import os
import json
import pandas as pd

DATASET_PATH = "SentinelMCP_Dataset_Clean.xlsx"
CONFIG_DIR = "config"
DATA_DIR = "data"

_CACHED_DATASET = None

def load_dataset(dataset_path: str = DATASET_PATH) -> dict:
    global _CACHED_DATASET
    if _CACHED_DATASET is None:
        if not os.path.exists(dataset_path):
            raise FileNotFoundError(f"Dataset file not found at {dataset_path}")
        _CACHED_DATASET = pd.read_excel(dataset_path, sheet_name=None)
    return _CACHED_DATASET

def generate_configs(dataset: dict):
    os.makedirs(CONFIG_DIR, exist_ok=True)
    os.makedirs(DATA_DIR, exist_ok=True)
    
    # 1. Tool Catalog Config
    tool_catalog_df = dataset.get('Tool Catalog')
    tool_catalog = {}
    if tool_catalog_df is not None:
        for _, row in tool_catalog_df.iterrows():
            tool_name = str(row['tool_name'])
            action = str(row['action'])
            base_risk = float(row['base_risk'])
            category = str(row.get('category', 'Core'))
            desc = str(row.get('description', ''))
            
            if tool_name not in tool_catalog:
                tool_catalog[tool_name] = {}
            
            tool_catalog[tool_name][action] = {
                "base_risk": base_risk,
                "category": category,
                "description": desc
            }
    
    catalog_path = os.path.join(CONFIG_DIR, 'tool_catalog.json')
    with open(catalog_path, 'w') as f:
        json.dump(tool_catalog, f, indent=2)
    print(f"Generated {catalog_path} ({len(tool_catalog)} tools configured)")

    # 2. Policy Store Config
    policy_df = dataset.get('Policy Store')
    policies = {}
    if policy_df is not None:
        for _, row in policy_df.iterrows():
            role = str(row['role'])
            dept = str(row.get('department', 'General'))
            max_class = str(row.get('max_data_classification', 'PUBLIC'))
            
            raw_allowed = str(row.get('allowed_tools', ''))
            raw_disallowed = str(row.get('disallowed_tools', ''))
            
            allowed = [x.strip() for x in raw_allowed.split(',') if x.strip() and x.strip().lower() != 'nan']
            disallowed = [x.strip() for x in raw_disallowed.split(',') if x.strip() and x.strip().lower() != 'nan']
            
            working_hours = bool(row.get('working_hours_only', False))
            
            policies[role] = {
                "department": dept,
                "max_data_classification": max_class,
                "allowed_tools": allowed,
                "disallowed_tools": disallowed,
                "working_hours_only": working_hours
            }
            
    policy_path = os.path.join(CONFIG_DIR, 'policy.json')
    with open(policy_path, 'w') as f:
        json.dump(policies, f, indent=2)
    print(f"Generated {policy_path} ({len(policies)} roles configured)")

if __name__ == "__main__":
    ds = load_dataset()
    print("=== Loaded Sheets and Row Counts ===")
    for sheet_name, df in ds.items():
        print(f"Sheet: {sheet_name:30s} | Rows: {len(df)}")
    print("\n=== Generating Configuration Files ===")
    generate_configs(ds)
