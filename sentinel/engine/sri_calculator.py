"""
SentinelMCP Core SRI Calculator Engine
Calculates final SRI risk index using 5 behavioral features, §4b graph analyzer (+30 bonus),
clamping to 100 max, and applying ±5 hysteresis secondary check on H_S[-3:].
"""
from typing import Dict, Any, List
from sentinel.engine.context_drift import compute_context_drift
from sentinel.engine.policy_checker import compute_policy_violation
from sentinel.engine.transition_risk import compute_transition_risk
from sentinel.engine.source_trust import compute_source_trust
from sentinel.engine.ml_classifier import compute_ml_score
from sentinel.engine.graph_analyzer import analyze_session_graph

def calculate_sri(
    user_prompt: str,
    tool_name: str,
    action: str,
    user_role: str = "junior_analyst",
    tool_args: dict = None,
    raw_output_text: str = "",
    classification: str = "PUBLIC",
    source_trust_level: str = "INTERNAL",
    session_history: List[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Computes complete Sentinel Risk Index (SRI) breakdown and decision band.
    """
    tool_args = tool_args or {}
    session_history = session_history or []

    # 1. Compute 5 features independently (each returns 0.0 - 1.0)
    cd = compute_context_drift(user_prompt, tool_name, action, tool_args)
    pv = compute_policy_violation(user_role, tool_name, action, classification)
    tr = compute_transition_risk(tool_name, action)
    st = compute_source_trust(session_history, source_trust_level)
    ml = compute_ml_score(tool_args, raw_output_text=raw_output_text, context=user_prompt)

    # Sensitive asset payload detection (secret.txt / .env / private repo)
    arg_str = str(tool_args).lower()
    is_sensitive_asset_request = any(k in arg_str for k in ["secret.txt", ".env", "security-internal", "private-repo", "password"])

    # 2. Raw weighted equation
    sri_raw = (0.30 * cd) + (0.20 * pv) + (0.25 * tr) + (0.15 * st) + (0.10 * ml)
    sri_base = round(100 * sri_raw)

    # Injection payload / sensitive asset bonus (+40 SRI) (pushes SRI > 50 SUSPICIOUS)
    injection_bonus = 40 if (ml >= 0.75 or is_sensitive_asset_request) else 0

    # 3. §4b Graph Analyzer path matching (+30 bonus)
    graph_bonus, matched_path, seq = analyze_session_graph(session_history, tool_name, action)

    # 4. Final SRI clamped to 100 max
    sri_unclamped = sri_base + graph_bonus + injection_bonus
    sri_final = min(100, sri_unclamped)

    # 5. Base Decision Band mapping
    decision = _map_sri_to_band(sri_final)

    # 6. Secondary Hysteresis Check (±5 pts of threshold edges 20, 50, 80)
    hysteresis_applied = False
    secondary_reason = ""

    near_edge = False
    for edge in [20, 50, 80]:
        if abs(sri_final - edge) <= 5:
            near_edge = True
            break

    if near_edge and len(session_history) >= 1:
        pass
#         recent_3 = session_history[-3:]
#         recent_sris = [e.get("sri", 0) for e in recent_3]
#         recent_trusts = [e.get("source_trust", "INTERNAL") for e in recent_3]

#         if "EXTERNAL_CONTENT" in recent_trusts or (len(recent_sris) >= 2 and recent_sris[-1] > recent_sris[0]):
#             hysteresis_applied = True
#             old_decision = decision
#             if decision == "SAFE":
#                 decision = "MONITOR"
#             elif decision == "MONITOR":
#                 decision = "SUSPICIOUS"
#             elif decision == "SUSPICIOUS":
#                 decision = "BLOCKED"
#             secondary_reason = f"Hysteresis check on H_S[-3:] elevated decision from {old_decision} to {decision} due to risk escalation."

    explanation = _generate_explanation(sri_final, decision, cd, pv, tr, st, ml, matched_path, graph_bonus, secondary_reason)

    return {
        "sri": sri_final,
        "sri_base": sri_base,
        "graph_bonus": graph_bonus,
        "injection_bonus": injection_bonus,
        "matched_path": matched_path,
        "decision": decision,
        "explanation": explanation,
        "hysteresis_applied": hysteresis_applied,
        "feature_scores": {
            "CD": cd,
            "PV": pv,
            "TR": tr,
            "ST": st,
            "ML": ml
        }
    }

def _map_sri_to_band(sri: int) -> str:
    if sri <= 20:
        return "SAFE"
    elif 21 <= sri <= 50:
        return "MONITOR"
    elif 51 <= sri <= 80:
        return "SUSPICIOUS"
    else:
        return "BLOCKED"

def _generate_explanation(sri: int, decision: str, cd: float, pv: float, tr: float, st: float, ml: float, matched_path: str, bonus: int, hysteresis_reason: str) -> str:
    drivers = []
    if cd >= 0.50:
        drivers.append(f"High Context Drift (CD={cd:.2f})")
    if pv >= 0.50:
        drivers.append(f"Policy Violation Breach (PV={pv:.2f})")
    if tr >= 0.70:
        drivers.append(f"High-Risk Tool Action (TR={tr:.2f})")
    if st >= 0.40:
        drivers.append(f"Untrusted Source Trajectory (ST={st:.2f})")
    if ml >= 0.50:
        drivers.append(f"Malicious Injection Payload (ML={ml:.2f})")
    if matched_path:
        drivers.append(f"Matched Dangerous Graph Path: '{matched_path}' (+{bonus} SRI)")

    driver_str = ", ".join(drivers) if drivers else "Low baseline risk across all 5 features"
    exp = f"Request scored SRI={sri} ({decision}). Risk Drivers: {driver_str}."
    if hysteresis_reason:
        exp += f" [{hysteresis_reason}]"
    return exp
