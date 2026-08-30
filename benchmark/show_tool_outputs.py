"""
SentinelMCP Milestone 2 Detailed Tool Outputs Verification
Calls each tool through sentinel/interceptor.py and displays real literal cell values loaded straight from SentinelMCP_Dataset_Clean.xlsx.
"""
import sys
import os
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sentinel.interceptor import intercept_tool_call

def run_real_seeds_demo():
    print("======================================================================")
    print("         SentinelMCP 7 Tools Interception & Real Cell Values Demo")
    print("======================================================================\n")

    calls = [
        # (a) Database Tool returning Alice Smith's real row
        {
            "title": "(a) Database Tool: Returning Alice Smith's Real Employee Row",
            "request": {
                "tool_name": "database_tool",
                "action": "query_select",
                "user_role": "junior_analyst",
                "context": "Query employees table for Engineering department",
                "args": {"table": "Employees", "query": "SELECT * FROM Employees"},
                "session_id": "sess_db_demo"
            }
        },
        # (b) GitHub Tool returning Issue #2 with its full real body text
        {
            "title": "(b) GitHub Tool: Issue #2 with Full Real Body Text (Prompt Injection)",
            "request": {
                "tool_name": "github_tool",
                "action": "read_issue",
                "user_role": "developer",
                "context": "Inspect open GitHub issue #2",
                "args": {"issue_id": 2, "repo": "core-backend"},
                "session_id": "sess_github_demo"
            }
        },
        # (c) Email Client / HTTP Tool returning the real body of the poisoned email MSG-1002
        {
            "title": "(c) Email Client / HTTP Tool: Real Body of Poisoned Email (secret.txt Exfiltration)",
            "request": {
                "tool_name": "http_tool",
                "action": "send_request",
                "user_role": "developer",
                "context": "Read inbox email MSG-1002",
                "args": {"email_id": "MSG-1002", "endpoint": "https://api.external.com/emails"},
                "session_id": "sess_email_demo"
            }
        },
        # PDF Reader
        {
            "title": "PDF Reader: Real PDF Docs Seed Cell Row",
            "request": {
                "tool_name": "pdf_reader",
                "action": "read_pdf",
                "user_role": "junior_analyst",
                "context": "Read document 1",
                "args": {"doc_id": 1},
                "session_id": "sess_pdf_demo"
            }
        },
        # Filesystem Tool
        {
            "title": "Filesystem Tool: Real Enterprise DB - Files Cell Row",
            "request": {
                "tool_name": "file_tool",
                "action": "read_file",
                "user_role": "junior_analyst",
                "context": "Read secret.txt file",
                "args": {"filepath": "secret.txt"},
                "session_id": "sess_file_demo"
            }
        },
        # Slack Tool
        {
            "title": "Slack Tool: Real Slack Seed Cell Row",
            "request": {
                "tool_name": "slack_tool",
                "action": "send_message",
                "user_role": "senior_analyst",
                "context": "Post to #general channel",
                "args": {"channel": "#general", "message": "Report status update"},
                "session_id": "sess_slack_demo"
            }
        },
        # Web Tool
        {
            "title": "Web Tool: Real Web Pages Seed Cell Row",
            "request": {
                "tool_name": "web_tool",
                "action": "fetch_page",
                "user_role": "developer",
                "context": "Fetch web page content",
                "args": {"url": "https://example.com/page1"},
                "session_id": "sess_web_demo"
            }
        }
    ]

    for item in calls:
        print(f"=== {item['title']} ===")
        res = intercept_tool_call(item["request"])
        tool_res = res["tool_result"]
        print(f"Interception Decision : {res['decision']} (SRI Score: {res['sri']})")
        print(f"Explanation           : {res['explanation']}")
        print(f"Source Excel Sheet    : {tool_res.get('source_sheet', 'N/A')}")
        print("Full Literal Tool Response Output:")
        print(json.dumps(tool_res, indent=2))
        print("\n" + "=" * 70 + "\n")

if __name__ == "__main__":
    run_real_seeds_demo()
