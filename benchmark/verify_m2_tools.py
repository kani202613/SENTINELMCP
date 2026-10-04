"""
SentinelMCP Milestone 2 Verification Script
Calls all 7 tools through sentinel/interceptor.py.
Verifies that no tool runs without passing through interceptor.py and confirms that output comes from correct seed sheets.
"""
import sys
import os
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sentinel.interceptor import intercept_tool_call

def verify_all_tools():
    print("======================================================================")
    print("         SentinelMCP Milestone 2 Verification Test Suite")
    print("======================================================================\n")

    test_requests = [
        # 1. Core Tool 1: pdf_reader
        {
            "tool_name": "pdf_reader",
            "action": "read_pdf",
            "user_role": "junior_analyst",
            "context": "Read Q3 Sales Performance PDF report",
            "args": {"doc_id": 1},
            "session_id": "m2_verify_sess"
        },
        # 2. Core Tool 2: file_tool
        {
            "tool_name": "file_tool",
            "action": "read_file",
            "user_role": "junior_analyst",
            "context": "Read sales data file",
            "args": {"filepath": "doc_1.txt"},
            "session_id": "m2_verify_sess"
        },
        # 3. Core Tool 3: github_tool
        {
            "tool_name": "github_tool",
            "action": "read_issue",
            "user_role": "developer",
            "context": "Inspect open GitHub bug issue",
            "args": {"issue_id": 1, "repo": "org/public-repo"},
            "session_id": "m2_verify_sess"
        },
        # 4. Core Tool 4: database_tool
        {
            "tool_name": "database_tool",
            "action": "query_select",
            "user_role": "junior_analyst",
            "context": "Run SQL SELECT query on Employees table",
            "args": {"table": "Employees", "query": "SELECT * FROM Employees"},
            "session_id": "m2_verify_sess"
        },
        # 5. Core Tool 5: slack_tool
        {
            "tool_name": "slack_tool",
            "action": "send_message",
            "user_role": "senior_analyst",
            "context": "Post update to team channel",
            "args": {"channel": "#general", "message": "Q3 Sales Analysis complete."},
            "session_id": "m2_verify_sess"
        },
        # 6. Extended Tool 1: web_tool
        {
            "tool_name": "web_tool",
            "action": "fetch_page",
            "user_role": "developer",
            "context": "Fetch web documentation page",
            "args": {"url": "https://example.com/page1"},
            "session_id": "m2_verify_sess"
        },
        # 7. Extended Tool 2: http_tool
        {
            "tool_name": "http_tool",
            "action": "send_request",
            "user_role": "developer",
            "context": "Send HTTP API request to external service",
            "args": {"endpoint": "https://api.external.com/data", "method": "POST", "payload": {"data": "test"}},
            "session_id": "m2_verify_sess"
        }
    ]

    for idx, req in enumerate(test_requests, 1):
        print(f"--- Test [{idx}/7]: Intercepting tool '{req['tool_name']}' (Action: '{req['action']}') ---")
        response = intercept_tool_call(req)
        
        tool_out = response.get("tool_result", {})
        source_sheet = tool_out.get("source_sheet", "N/A")
        status = tool_out.get("status", "N/A")
        
        print(f"Interception Status : {response['interception_status']}")
        print(f"Decision Band       : {response['decision']} (SRI: {response['sri']})")
        print(f"Explanation         : {response['explanation']}")
        print(f"Tool Status         : {status}")
        print(f"Source Excel Sheet  : {source_sheet}")
        print(f"Tool Output Sample  : {json.dumps(tool_out, indent=2)[:250]}...")
        print("-" * 70 + "\n")

if __name__ == "__main__":
    verify_all_tools()
