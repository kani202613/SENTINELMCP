"""
SentinelMCP — Enterprise Tool Base Class & Data Provider (Milestone 2)
Provides shared seed data access for all 7 enterprise tools.
"""
import os
import pandas as pd
from data_loader import load_dataset, DATASET_PATH

class ToolDataProvider:
    _dataset = None

    @classmethod
    def get_dataset(cls) -> dict:
        if cls._dataset is None:
            cls._dataset = load_dataset()
        return cls._dataset

    @classmethod
    def get_sheet(cls, sheet_name: str) -> pd.DataFrame:
        ds = cls.get_dataset()
        if sheet_name not in ds:
            raise KeyError(f"Sheet '{sheet_name}' not found in dataset.")
        return ds[sheet_name]
