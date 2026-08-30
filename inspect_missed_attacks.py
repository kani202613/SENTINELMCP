"""
Inspect the 21 Missed Attack sessions (False Negatives).
Displays Session ID, Sheet, Category, User Prompt, Step Sequence, Feature Scores, and why it was missed.
"""
import sys
import os
import json
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sentinel.interceptor import SentinelInterceptor

def normalize_tool_request(step: dict) -> tuple:
    raw_tool = str(step.get("tool_name", "file_tool")).lower()
    args = step.get("args", {})
    action = str(step.get("action", args.get("action", ""))).lower()

    if raw_tool in ["file_reader", "file_writer", "file_client"]:
        tool_name = "file_tool"
        action = action or ("read_file" if "read" in raw_tool else "write_file")
    elif raw_tool in ["email_client", "http_client", "api_client", "http_tool"]:
        tool_name = "http_tool"
        action = action or "send_request"
    elif raw_tool in ["github_client", "github_tool"]:
        tool_name = "github_tool"
        action = action or "read_issue"
    elif raw_tool in ["web_browser", "web_tool"]:
        tool_name = "web_tool"
        action = action or "fetch_page"
    elif raw_tool in ["database_client", "sql_client", "database_tool"]:
        tool_name = "database_tool"
        action = action or "query_select"
    elif raw_tool in ["pdf_reader", "pdf_client"]:
        tool_name = "pdf_reader"
        action = action or "read_pdf"
    elif raw_tool in ["slack_client", "slack_tool"]:
        tool_name = "slack_tool"
        action = action or "send_message"
    else:
        tool_name = "file_tool"
        action = action or "read_file"

    return tool_name, action

def inspect_missed_attacks():
    excel_path = "SentinelMCP_Dataset_Clean.xlsx"
    xl = pd.ExcelFile(excel_path)

    attack_traces = []
    for sheet in ["Traces - Main", "Traces - Set B (Red-Team)", "Traces - Evasion"]:
        if sheet in xl.sheet_names:
            df = pd.read_excel(excel_path, sheet_name=sheet)
            for idx, r in df.iterrows():
                if str(r['Label']) == "ATTACK":
                    try:
                        steps = json.loads(str(r['Raw Trace Details']))
                        attack_traces.append({
                            "session_id": str(r['Session ID']),
                            "category": str(r.get('Attack Category', 'General')),
                            "user_prompt": str(r['User Prompt']),
                            "steps": steps,
                            "sheet": sheet
                        })
                    except Exception:
                        pass

    fns = []
    for trace in attack_traces:
        interceptor = SentinelInterceptor(audit_log_path="data/audit_log.json")
        session_id = trace["session_id"]
        user_prompt = trace["user_prompt"]
        steps = trace["steps"]

        max_sri = 0
        final_decision = "SAFE"
        last_step_info = None

        for step in steps:
            tool_name, action = normalize_tool_request(step)
            args = step.get("args", {})
            source_trust = str(step.get("source_trust", "INTERNAL"))

            req = {
                "tool_name": tool_name,
                "action": action,
                "user_role": "junior_analyst",
                "context": user_prompt,
                "args": args,
                "session_id": session_id,
                "source_trust": source_trust
            }

            res = interceptor.intercept_and_execute(req)
            sri_details = res["sri_details"]
            sri = sri_details["sri"]
            dec = res["decision"]

            if sri > max_sri:
                max_sri = sri
                final_decision = dec
                last_step_info = {
                    "tool_name": tool_name,
                    "action": action,
                    "source_trust": source_trust,
                    "sri": sri,
                    "decision": dec,
                    "explanation": res["explanation"],
                    "features": sri_details["feature_scores"],
                    "matched_path": sri_details["matched_path"]
                }

        if final_decision in ["SAFE", "MONITOR"]:
            fns.append({
                "session_id": session_id,
                "sheet": trace["sheet"],
                "category": trace["category"],
                "user_prompt": user_prompt,
                "max_sri": max_sri,
                "decision": final_decision,
                "step_info": last_step_info,
                "step_sequence": [f"{s.get('tool_name')}.{s.get('action')}" for s in steps]
            })

    print("==================================================================================")
    print(f"            FOUND {len(fns)} MISSED ATTACK SESSIONS (FALSE NEGATIVES)")
    print("==================================================================================\n")

    for i, fn in enumerate(fns, 1):
        info = fn["step_info"]
        f = info["features"]
        seq_str = " -> ".join(fn["step_sequence"])
        print(f"[{i}/{len(fns)}] Session ID: {fn['session_id']} | Sheet: {fn['sheet']} | Category: {fn['category']}")
        print(f"    User Prompt  : '{fn['user_prompt']}'")
        print(f"    Sequence     : {seq_str}")
        print(f"    Features     : CD={f['CD']:.2f} | PV={f['PV']:.2f} | TR={f['TR']:.2f} | ST={f['ST']:.2f} | ML={f['ML']:.2f}")
        print(f"    Matched Path : '{info['matched_path'] or 'None'}'")
        print(f"    Final SRI    : {info['sri']} ({fn['decision']})")
        print("----------------------------------------------------------------------------------")

if __name__ == "__main__":
    inspect_missed_attacks()
