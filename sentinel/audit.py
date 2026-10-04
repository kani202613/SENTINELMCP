"""
SentinelMCP Explanation Generator & Permanent Audit Logger (Optimized Infrastructure)
Generates human-readable explanations and writes high-performance JSON Lines (.jsonl) audit logs.
"""
import os
import json
import time
from typing import Dict, Any

class AuditLogger:
    def __init__(self, log_path: str = "data/m5_audit_log.jsonl"):
        self.log_path = log_path
        os.makedirs(os.path.dirname(self.log_path), exist_ok=True)

    def log_event(
        self,
        session_id: str,
        user_role: str,
        tool_name: str,
        action: str,
        args: dict,
        sri_res: dict,
        scoring_latency_ms: float,
        tool_result: dict,
        total_latency_ms: float = 0.0,
        approval_status: str = "N/A"
    ) -> Dict[str, Any]:
        """
        Constructs and records audit log entry into JSON Lines format (.jsonl).
        """
        sri = sri_res.get("sri", 0)
        decision = sri_res.get("decision", "SAFE")
        explanation = self.generate_explanation(sri_res, tool_name, action)
        
        entry = {
            "entry_id": f"audit_{os.urandom(4).hex()}",
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "session_id": session_id,
            "user_role": user_role,
            "tool_name": tool_name,
            "action": action,
            "args": args,
            "sri": sri,
            "decision": decision,
            "explanation": explanation,
            "feature_breakdown": sri_res.get("feature_scores", {}),
            "matched_path": sri_res.get("matched_path", ""),
            "graph_bonus": sri_res.get("graph_bonus", 0),
            "injection_bonus": sri_res.get("injection_bonus", 0),
            "hysteresis_applied": sri_res.get("hysteresis_applied", False),
            "scoring_latency_ms": scoring_latency_ms,
            "total_latency_ms": total_latency_ms or scoring_latency_ms,
            "sandboxed": tool_result.get("sandboxed", False) if isinstance(tool_result, dict) else False,
            "approval_status": approval_status,
            "tool_result": tool_result
        }

        self._append_to_jsonl(entry)
        return entry

    def generate_explanation(self, sri_res: dict, tool_name: str, action: str) -> str:
        """
        Generates human-readable explanation naming driving risk features and matched graph paths.
        """
        sri = sri_res.get("sri", 0)
        decision = sri_res.get("decision", "SAFE")
        f = sri_res.get("feature_scores", {})
        matched_path = sri_res.get("matched_path", "")
        graph_bonus = sri_res.get("graph_bonus", 0)
        hysteresis_applied = sri_res.get("hysteresis_applied", False)

        drivers = []
        if f.get("CD", 0) >= 0.50:
            drivers.append(f"High Context Drift (CD={f.get('CD'):.2f})")
        if f.get("PV", 0) >= 0.50:
            drivers.append(f"Policy Violation Breach (PV={f.get('PV'):.2f})")
        if f.get("TR", 0) >= 0.70:
            drivers.append(f"High-Risk Tool Action (TR={f.get('TR'):.2f})")
        if f.get("ST", 0) >= 0.40:
            drivers.append(f"Untrusted Source Trajectory (ST={f.get('ST'):.2f})")
        if f.get("ML", 0) >= 0.50:
            drivers.append(f"Malicious Injection Payload (ML={f.get('ML'):.2f})")

        if matched_path:
            drivers.append(f"Matched Dangerous Graph Path '{matched_path}' (+{graph_bonus} SRI)")

        driver_text = ", ".join(drivers) if drivers else "Low baseline risk across all 5 features"

        exp = f"Request for '{tool_name}.{action}' evaluated SRI={sri} ({decision}). Risk Drivers: {driver_text}."
        if hysteresis_applied:
            exp += " [Hysteresis secondary check elevated risk band due to session escalation trend.]"

        return exp

    def _append_to_jsonl(self, entry: dict):
        """Append-only high-speed JSON Lines logger."""
        try:
            with open(self.log_path, "a") as f:
                f.write(json.dumps(entry) + "\n")
        except Exception:
            pass

_audit_logger_instance = AuditLogger()

def log_audit_event(session_id: str, user_role: str, tool_name: str, action: str, args: dict, sri_res: dict, scoring_latency_ms: float, tool_result: dict, total_latency_ms: float = 0.0, approval_status: str = "N/A") -> dict:
    return _audit_logger_instance.log_event(session_id, user_role, tool_name, action, args, sri_res, scoring_latency_ms, tool_result, total_latency_ms, approval_status)
