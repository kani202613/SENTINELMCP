"""
SentinelMCP Risk Engine — Feature 1: Context Drift (CD)
Evaluates semantic divergence between User Stated Intent and Tool Call Action.
"""
import re
import math
from collections import Counter

def compute_context_drift(user_prompt: str, tool_name: str, action: str, tool_args: dict = None) -> float:
    """
    Computes Context Drift score (0.0 to 1.0).
    0.0 = High semantic alignment between user intent and tool call.
    1.0 = High drift / explicit semantic mismatch.
    """
    if not user_prompt:
        return 0.20

    prompt_lower = user_prompt.lower()
    args_text = " ".join([f"{k} {v}" for k, v in (tool_args or {}).items() if isinstance(v, (str, int, float))]).lower()
    tool_text = f"{tool_name} {action} {args_text}".strip().lower()

    # 1. Check explicit destructive / privilege escalation mismatches
    if ("delete" in action or "delete" in tool_name) and "delete" not in prompt_lower and "remove" not in prompt_lower:
        return 0.90
    if ("write" in action or "update" in action) and "write" not in prompt_lower and "create" not in prompt_lower and "update" not in prompt_lower and "save" not in prompt_lower:
        return 0.75
    if ("private" in action or "secret" in args_text or "secret" in tool_text) and "secret" not in prompt_lower and "private" not in prompt_lower:
        return 0.85

    # 2. Check standard benign tool alignment
    # If tool is a standard read/search tool for a benign user query, drift is low
    read_tools = ["read_file", "read_pdf", "read_issue", "query_select", "fetch_page", "read", "send_request"]
    if action in read_tools or any(rt in action for rt in ["read", "select", "fetch", "query"]):
        # Check term overlap
        words1 = set(re.findall(r'\w+', prompt_lower))
        words2 = set(re.findall(r'\w+', tool_text))
        
        # Filter common stopwords
        stopwords = {"what", "is", "the", "like", "today", "my", "from", "for", "a", "an", "in", "to", "on", "our", "repo"}
        w1 = words1 - stopwords
        w2 = words2 - stopwords
        
        if not w1 or not w2:
            return 0.10
            
        overlap = len(w1 & w2)
        if overlap > 0:
            return 0.05
        else:
            # Benign read action without keyword overlap
            return 0.15

    return 0.25
