"""
SentinelMCP Risk Engine — Feature 3: Tool Transition Risk (TR)
Lookup table from config/tool_catalog.json for tool/action base risk.
"""
import os
import json

class TransitionRiskEvaluator:
    def __init__(self, catalog_path: str = "config/tool_catalog.json"):
        self.catalog_path = catalog_path
        self.catalog = self._load_catalog()

    def _load_catalog(self) -> dict:
        if os.path.exists(self.catalog_path):
            try:
                with open(self.catalog_path) as f:
                    return json.load(f)
            except Exception:
                pass
        return {}

    def compute_transition_risk(self, tool_name: str, action: str) -> float:
        """
        Computes Tool Transition Risk score (0.0 to 1.0) from lookup table.
        """
        if not self.catalog:
            self.catalog = self._load_catalog()

        tool_entry = self.catalog.get(tool_name, {})
        if isinstance(tool_entry, dict) and action in tool_entry:
            return float(tool_entry[action].get("base_risk", 0.30))

        # Default fallback heuristics
        if "delete" in action or "delete" in tool_name:
            return 0.85
        elif "write" in action or "update" in action or "private" in action:
            return 0.65
        elif "send" in action or "http" in tool_name:
            return 0.40
        elif "read" in action or "select" in action:
            return 0.15

        return 0.25

_tr_instance = TransitionRiskEvaluator()

def compute_transition_risk(tool_name: str, action: str) -> float:
    return _tr_instance.compute_transition_risk(tool_name, action)
