"""
SentinelMCP Milestone 8 — Empirical Ablation Study (benchmark/ablation_study.py)
Evaluates the frozen 127-trace benchmark across 7 ablation configurations:
1. Full Model (Frozen Baseline: 76 TP, 0 FP, 46 TN, 5 FN -> F1 = 96.82%)
2. Without Context Drift (CD = 0)
3. Without Policy Violation (PV = 0)
4. Without Transition Risk (TR = 0)
5. Without Source Trust (ST = 0)
6. Without ML Content Scanner (ML = 0)
7. Without Session Graph Analyzer (graph_bonus = 0)

Computes Accuracy, Precision, Recall, F1-Score, FPR, TP, FP, TN, FN, and Delta F1 relative to Full Model.
Uses REAL empirical trace replay results only.
"""
import os
import sys
import json
import pandas as pd
import numpy as np
from typing import Dict, Any

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sentinel.engine.sri_calculator import calculate_sri, _map_sri_to_band
from sentinel.engine.policy_checker import compute_policy_violation
from sentinel.engine.graph_analyzer import analyze_session_graph
from benchmark.eval_harness import normalize_tool_request

def run_ablation_experiment(ablate_feature: str = None) -> Dict[str, Any]:
    excel_path = "SentinelMCP_Dataset_Clean.xlsx"
    xl = pd.ExcelFile(excel_path)

    trace_sessions = []
    for sheet in ["Traces - Main", "Traces - Set B (Red-Team)", "Traces - Evasion"]:
        if sheet in xl.sheet_names:
            df = pd.read_excel(excel_path, sheet_name=sheet)
            for idx, r in df.iterrows():
                try:
                    steps = json.loads(str(r['Raw Trace Details']))
                    trace_sessions.append({
                        "session_id": str(r.get("Trace ID", f"trace_{idx}")),
                        "user_prompt": str(r.get("User Prompt", "")),
                        "label": str(r.get("Label", "BENIGN")).upper(),
                        "category": str(r.get("Category", "Unknown")),
                        "steps": steps
                    })
                except Exception:
                    pass

    tp = fp = tn = fn = 0

    for trace in trace_sessions:
        session_id = trace["session_id"]
        is_attack = (trace["label"] == "ATTACK")
        user_prompt = trace["user_prompt"]
        steps = trace["steps"]

        max_sri = 0
        final_decision = "SAFE"
        session_history = []

        for step in steps:
            tool_name, action = normalize_tool_request(step)
            args = step.get("args", {})
            source_trust = str(step.get("source_trust", "INTERNAL"))

            # Standard SRI calculation
            sri_res = calculate_sri(
                user_prompt=user_prompt,
                tool_name=tool_name,
                action=action,
                user_role="junior_analyst",
                tool_args=args,
                raw_output_text="",
                classification="PUBLIC",
                source_trust_level=source_trust,
                session_history=session_history
            )

            f = dict(sri_res["feature_scores"])

            # Feature ablation override
            if ablate_feature in ["CD", "PV", "TR", "ST", "ML"]:
                f[ablate_feature] = 0.0

            # Re-compute SRI base score (weighted equation: 0.30*cd + 0.20*pv + 0.25*tr + 0.15*st + 0.10*ml)
            sri_raw = (0.30 * f["CD"]) + (0.20 * f["PV"]) + (0.25 * f["TR"]) + (0.15 * f["ST"]) + (0.10 * f["ML"])
            sri_base = round(100 * sri_raw)

            # Sensitive asset / injection payload bonus (+40 SRI)
            arg_str = str(args).lower()
            is_sensitive_asset_request = any(k in arg_str for k in ["secret.txt", ".env", "security-internal", "private-repo", "password"])
            injection_bonus = 50 if (f["ML"] >= 0.75 or is_sensitive_asset_request) else 0

            # Graph analyzer ablation
            if ablate_feature == "GRAPH":
                graph_bonus = 0
                matched_path = ""
            else:
                graph_bonus, matched_path, _ = analyze_session_graph(session_history, tool_name, action)

            if ablate_feature is None:
                # Full Model uses exact calculate_sri output
                final_sri = sri_res["sri"]
                decision = sri_res["decision"]
            else:
                final_sri = min(100, sri_base + graph_bonus + injection_bonus)
                decision = _map_sri_to_band(final_sri)

                # Hysteresis escalation check
                near_edge = any(abs(final_sri - edge) <= 5 for edge in [20, 50, 80])
                if near_edge and len(session_history) >= 1:
                    recent_3 = session_history[-3:]
                    recent_sris = [e.get("sri", 0) for e in recent_3]
                    recent_trusts = [e.get("source_trust", "INTERNAL") for e in recent_3]

                    if "EXTERNAL_CONTENT" in recent_trusts or (len(recent_sris) >= 2 and recent_sris[-1] > recent_sris[0]):
                        if decision == "SAFE":
                            decision = "MONITOR"
                        elif decision == "MONITOR":
                            decision = "SUSPICIOUS"
                        elif decision == "SUSPICIOUS":
                            decision = "BLOCKED"

            if decision in ["SUSPICIOUS", "BLOCKED"] or final_sri > max_sri:
                max_sri = final_sri
                final_decision = decision

            session_history.append({
                "tool_name": tool_name,
                "action": action,
                "sri": final_sri,
                "decision": decision,
                "source_trust": source_trust
            })

        system_flagged = (final_decision in ["SUSPICIOUS", "BLOCKED"])

        if is_attack:
            if system_flagged:
                tp += 1
            else:
                fn += 1
        else:
            if system_flagged:
                fp += 1
            else:
                tn += 1

    total = tp + fp + tn + fn
    accuracy = (tp + tn) / total * 100 if total > 0 else 0.0
    precision = tp / (tp + fp) * 100 if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) * 100 if (tp + fn) > 0 else 0.0
    f1 = (2 * precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
    fpr = fp / (fp + tn) * 100 if (fp + tn) > 0 else 0.0

    return {
        "ablation": ablate_feature or "FULL_MODEL",
        "total": total,
        "tp": tp,
        "fp": fp,
        "tn": tn,
        "fn": fn,
        "accuracy": accuracy,
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "fpr": fpr
    }

def run_full_ablation_study():
    print("==================================================================================")
    print("            SentinelMCP Milestone 8: Empirical Ablation Study")
    print("==================================================================================\n")

    ablations = [
        (None, "Full Model (Frozen Baseline)"),
        ("CD", "Without Context Drift (CD = 0)"),
        ("PV", "Without Policy Violation (PV = 0)"),
        ("TR", "Without Transition Risk (TR = 0)"),
        ("ST", "Without Source Trust (ST = 0)"),
        ("ML", "Without ML Content Scanner (ML = 0)"),
        ("GRAPH", "Without Session Graph Analyzer (Graph = 0)")
    ]

    results = []
    baseline_f1 = 0.0

    for key, name in ablations:
        res = run_ablation_experiment(ablate_feature=key)
        res["name"] = name
        if key is None:
            baseline_f1 = res["f1"]
            res["delta_f1"] = 0.0
        else:
            res["delta_f1"] = res["f1"] - baseline_f1
        results.append(res)

    print(f"{'Configuration':<42} {'Acc (%)':>8} {'Prec (%)':>9} {'Rec (%)':>8} {'F1 (%)':>8} {'FPR (%)':>8} {'Delta F1':>9} {'TP/FP/TN/FN':>14}")
    print("-" * 115)

    for r in results:
        counts_str = f"{r['tp']}/{r['fp']}/{r['tn']}/{r['fn']}"
        delta_str = f"{r['delta_f1']:+.2f}" if r['delta_f1'] != 0 else "0.00"
        print(f"{r['name']:<42} {r['accuracy']:>8.2f} {r['precision']:>9.2f} {r['recall']:>8.2f} {r['f1']:>8.2f} {r['fpr']:>8.2f} {delta_str:>9} {counts_str:>14}")

    print("\n==================================================================================")
    print("                ABLATION STUDY EXPERIMENT COMPLETE")
    print("==================================================================================\n")
    return results

if __name__ == "__main__":
    run_full_ablation_study()
