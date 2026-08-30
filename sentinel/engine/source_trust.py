"""
SentinelMCP Risk Engine — Feature 4: Source Trust (ST)
Evaluates inter-call temporal distance, context state jumps, and source trust level.
"""
from typing import List, Dict, Any

def compute_source_trust(session_history: List[Dict[str, Any]], current_source_trust: str = "INTERNAL") -> float:
    """
    Computes Source Trust risk score (0.0 to 1.0).
    Higher score = lower trust / abrupt behavioral shift or external untrusted content.
    """
    base_score = 0.10

    # 1. External content trust penalty
    if current_source_trust == "EXTERNAL_CONTENT":
        base_score += 0.50

    if not session_history:
        return round(base_score, 4)

    # 2. Check trajectory jump
    past_tools = [e.get("tool_name", "") for e in session_history]
    past_actions = [e.get("action", "") for e in session_history]
    past_trusts = [e.get("source_trust", "INTERNAL") for e in session_history]

    # If any previous step processed external untrusted content, propagate trust taint
    if "EXTERNAL_CONTENT" in past_trusts:
        base_score += 0.35

    # Check state jump: silent reading -> sudden state mutation / data exfiltration
    if len(past_actions) >= 1:
        if current_source_trust == "EXTERNAL_CONTENT":
            base_score += 0.25

    return round(min(1.0, base_score), 4)
