"""
SentinelMCP Milestone 3 — 10 Additional Sessions Replay Verification Suite
Replays 5 BENIGN sessions and 5 ATTACK sessions covering:
- POISONED_GITHUB_ISSUE
- CROSS_TOOL_PRIVILEGE_ESCALATION
- POISONED_SLACK
- POISONED_WEBSITE
- MALICIOUS_API_RESPONSE

Verifies that benign sessions mostly score SAFE (SRI <= 20) and all attack categories are caught (SUSPICIOUS/BLOCKED).
"""
import sys
import os
import json
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sentinel.interceptor import SentinelInterceptor, _interceptor_instance

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

def run_10_session_replay():
    print("==================================================================================")
    print("         SentinelMCP 10 Additional Sessions Trace Replay Suite")
    print("==================================================================================\n")

    excel_path = "SentinelMCP_Dataset_Clean.xlsx"
    if not os.path.exists(excel_path):
        print(f"Error: {excel_path} not found.")
        return

    df = pd.read_excel(excel_path, sheet_name="Traces - Main")

    # Select 5 BENIGN sessions
    benign_sessions = df[df['Label'] == 'BENIGN'].head(5)

    # Select 5 ATTACK sessions covering target categories
    target_cats = [
        "POISONED_GITHUB_ISSUE",
        "CROSS_TOOL_PRIVILEGE_ESCALATION",
        "POISONED_SLACK",
        "POISONED_WEBSITE",
        "MALICIOUS_API_RESPONSE"
    ]
    
    attack_rows = []
    for cat in target_cats:
        match = df[df['Attack Category'].astype(str).str.contains(cat, case=False, na=False)]
        if not match.empty:
            attack_rows.append(match.iloc[0])

    attack_sessions = pd.DataFrame(attack_rows)
    combined_sessions = pd.concat([benign_sessions, attack_sessions], ignore_index=True)

    interceptor = SentinelInterceptor(audit_log_path="data/audit_log.json")

    results_table = []

    for idx, row in combined_sessions.iterrows():
        session_id = str(row['Session ID'])
        label = str(row['Label'])
        category = str(row.get('Attack Category', 'BENIGN'))
        user_prompt = str(row['User Prompt'])
        raw_trace = str(row['Raw Trace Details'])

        expected_decision = "SAFE / MONITOR" if label == "BENIGN" else "BLOCKED / SUSPICIOUS"

        print(f"==================================================================================")
        print(f" SESSION [{idx+1}/10]: {session_id} | Label: {label} | Category: {category}")
        print(f" User Prompt: '{user_prompt}'")
        print(f" Expected Decision: {expected_decision}")
        print(f"----------------------------------------------------------------------------------")

        steps = []
        try:
            steps = json.loads(raw_trace)
        except Exception as e:
            print(f" Failed to parse trace details JSON: {e}")
            continue

        session_final_sri = 0
        session_final_decision = "SAFE"
        last_features = {}

        for step in steps:
            step_num = step.get("step", 1)
            tool_name, action = normalize_tool_request(step)
            args = step.get("args", {})
            source_trust = step.get("source_trust", "INTERNAL")

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
            f = sri_details["feature_scores"]
            last_features = f

            if sri_details["sri"] > session_final_sri:
                session_final_sri = sri_details["sri"]
                session_final_decision = res["decision"]

            print(f"  [Step {step_num}] Tool: '{tool_name}.{action}' | Source Trust: {source_trust}")
            print(f"    Features    : CD={f['CD']:.2f} | PV={f['PV']:.2f} | TR={f['TR']:.2f} | ST={f['ST']:.2f} | ML={f['ML']:.2f}")
            print(f"    Graph Bonus : +{sri_details['graph_bonus']} SRI (Matched: '{sri_details['matched_path'] or 'None'}')")
            print(f"    Final SRI   : {sri_details['sri']} (Base: {sri_details['sri_base']})")
            print(f"    Decision    : {res['decision']}")
            print(f"    Explanation : {res['explanation']}")
            print()

        # Compare session final verdict with expected label
        is_attack = label == "ATTACK"
        decision_correct = (is_attack and session_final_decision in ["SUSPICIOUS", "BLOCKED"]) or (not is_attack and session_final_decision in ["SAFE", "MONITOR"])
        match_status = "[PASS]" if decision_correct else "[REVIEW]"

        results_table.append({
            "Session ID": session_id,
            "Label": label,
            "Category": category,
            "User Prompt": user_prompt[:35] + "...",
            "CD": f"{last_features.get('CD', 0):.2f}",
            "PV": f"{last_features.get('PV', 0):.2f}",
            "TR": f"{last_features.get('TR', 0):.2f}",
            "ST": f"{last_features.get('ST', 0):.2f}",
            "ML": f"{last_features.get('ML', 0):.2f}",
            "Max SRI": session_final_sri,
            "Sentinel Verdict": session_final_decision,
            "Expected": expected_decision,
            "Status": match_status
        })

        print(f" Session Final Summary:")
        print(f"   Max Session SRI   : {session_final_sri}")
        print(f"   Sentinel Decision : {session_final_decision}")
        print(f"   Expected Decision : {expected_decision}")
        print(f"   Validation Status : {match_status}")
        print("==================================================================================\n")

    # Print Summary Table
    print("\n==================================================================================")
    print("                     SUMMARY TABLE (10 SESSIONS REPLAY)")
    print("==================================================================================")
    res_df = pd.DataFrame(results_table)
    print(res_df.to_string(index=False))

if __name__ == "__main__":
    run_10_session_replay()
