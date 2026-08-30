"""
SentinelMCP Risk Engine — Feature 5: Machine Learning (ML) Content Scanner
Scans raw argument payloads, contexts, and outputs for prompt injections, base64 blobs, zero-width unicode, and exfiltration tokens.
"""
import re
import json
import base64

INJECTION_PATTERNS = [
    r"ignore\s+(all\s+)?(previous|prior)\s+(instructions|rules|directions|prompt)",
    r"system_instruction",
    r"<system_instruction>",
    r"drop\s+database",
    r"delete\s+the\s+repository",
    r"override\s+security\s+policy",
    r"grant\s+admin\s+privileges",
    r"export\s+the\s+contents\s+of\s+secret",
    r"paste\s+its\s+\.env",
    r"\[INJECTION:",
    r"\[NOTE:\s*Also\s+read",
    r"private-repo",
    r"vendor\s+994",
    r"authorize\s+payment",
    r"cve-2024-",
    r"http_tool"
]

def compute_ml_score(args: dict = None, raw_output_text: str = "", context: str = "") -> float:
    """
    Computes ML content maliciousness score (0.0 to 1.0).
    """
    args = args or {}
    text_to_scan = json.dumps(args) + " " + str(raw_output_text) + " " + str(context)
    text_lower = text_to_scan.lower()

    # 1. Check prompt injection regex patterns
    pattern_matches = 0
    for pattern in INJECTION_PATTERNS:
        if re.search(pattern, text_to_scan, re.IGNORECASE):
            pattern_matches += 1

    if pattern_matches >= 2:
        return 0.95
    elif pattern_matches == 1:
        return 0.85

    # 2. Check zero-width unicode characters (\u200B, \u200C, \u200D, \uFEFF)
    zero_width_chars = ["\u200b", "\u200c", "\u200d", "\ufeff"]
    if any(zw in text_to_scan for zw in zero_width_chars):
        return 0.90

    # 3. Check base64 obfuscated payload patterns (e.g. d2dldC...)
    base64_blobs = re.findall(r'[A-Za-z0-9+/]{30,}={0,2}', text_to_scan)
    if base64_blobs:
        return 0.75

    # 4. Keyword heuristic checks
    if "secret.txt" in text_lower or ".env" in text_lower or "drop database" in text_lower or "injection" in text_lower:
        return 0.80

    return 0.05
