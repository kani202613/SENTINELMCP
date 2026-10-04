"""
SentinelMCP Database Sandbox Integrity Verification Test
Executes a SUSPICIOUS SQL DELETE attack query through Sentinel Interceptor and verifies that
the real 'Enterprise DB - Employees' Excel database remains completely unchanged.
"""
import sys
import os
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sentinel.interceptor import SentinelInterceptor

def verify_db_sandbox():
    print("==================================================================================")
    print("       SentinelMCP Database Sandbox Integrity Verification Test")
    print("==================================================================================\n")

    excel_path = "SentinelMCP_Dataset_Clean.xlsx"
    df_before = pd.read_excel(excel_path, sheet_name="Enterprise DB - Employees")
    row_count_before = len(df_before)
    alice_before = df_before[df_before['id'] == 'EMP-001'].to_dict(orient='records')

    print(f"Pre-Attack DB State : {row_count_before} Employee Rows")
    print(f"Pre-Attack Alice    : {alice_before[0]['name']} | {alice_before[0]['role']} | Salary: ${alice_before[0]['salary']}\n")

    interceptor = SentinelInterceptor(audit_log_path="data/audit_log.json")

    # Construct SUSPICIOUS SQL DELETE attack request
    attack_request = {
        "session_id": "sess_db_attack_test",
        "tool_name": "database_tool",
        "action": "query_delete",
        "user_role": "developer",
        "context": "Clean up employee records",
        "args": {
            "action": "query_delete",
            "query": "DELETE FROM Employees WHERE id = 'EMP-001'",
            "table": "Employees"
        },
        "source_trust": "INTERNAL"
    }

    print("Executing Malicious DB Query: 'DELETE FROM Employees WHERE id = 'EMP-001'' ...")
    res = interceptor.intercept_and_execute(attack_request)

    print(f"Sentinel Decision   : {res['decision']} (SRI: {res['sri']})")
    print(f"Explanation         : {res['explanation']}")
    print(f"Sandboxed Execution : {res['tool_result'].get('sandboxed', False)}")
    print(f"Sandbox Output Msg  : {res['tool_result'].get('message', 'N/A')}\n")

    # Re-read real Excel database sheet to verify 100% data integrity
    df_after = pd.read_excel(excel_path, sheet_name="Enterprise DB - Employees")
    row_count_after = len(df_after)
    alice_after = df_after[df_after['id'] == 'EMP-001'].to_dict(orient='records')

    print(f"Post-Attack DB State: {row_count_after} Employee Rows")
    print(f"Post-Attack Alice   : {alice_after[0]['name']} | {alice_after[0]['role']} | Salary: ${alice_after[0]['salary']}\n")

    is_intact = (row_count_before == row_count_after == 10) and (alice_after[0]['salary'] == 165000)
    status = "[PASS] Real Database Unchanged & Intact" if is_intact else "[FAIL] Database Mutated"
    
    print(f"Verification Result : {status}")
    print("==================================================================================\n")

if __name__ == "__main__":
    verify_db_sandbox()
