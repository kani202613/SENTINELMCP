"""
SentinelMCP Enterprise Tools Package (Milestone 3)
Exports all 7 tools (5 Core + 2 Extended) and robust unified execution handler.
"""
from tools.pdf_reader import read_pdf
from tools.file_tool import file_tool
from tools.github_tool import github_tool
from tools.database_tool import database_tool
from tools.slack_tool import slack_tool
from tools.web_tool import web_tool
from tools.http_tool import http_tool

TOOL_REGISTRY = {
    "pdf_reader": read_pdf,
    "file_tool": file_tool,
    "github_tool": github_tool,
    "database_tool": database_tool,
    "slack_tool": slack_tool,
    "web_tool": web_tool,
    "http_tool": http_tool
}

def execute_tool(tool_name: str, action: str = None, kwargs: dict = None, sandboxed: bool = False) -> dict:
    """Unified dispatcher for executing enterprise tools with robust argument mapping."""
    if tool_name not in TOOL_REGISTRY:
        raise ValueError(f"Tool '{tool_name}' is not registered in Enterprise Tools.")

    kwargs = kwargs or {}
    tool_fn = TOOL_REGISTRY[tool_name]

    if tool_name == "pdf_reader":
        doc_p = kwargs.get("doc_path", kwargs.get("filepath", kwargs.get("path", None)))
        doc_i = kwargs.get("doc_id", 1)
        return tool_fn(doc_path=doc_p, doc_id=doc_i)

    elif tool_name == "file_tool":
        act = action or kwargs.get("action", "read_file")
        fp = kwargs.get("filepath", kwargs.get("path", "secret.txt"))
        cnt = kwargs.get("content", "")
        return tool_fn(action=act, filepath=fp, content=cnt, sandboxed=sandboxed)

    elif tool_name == "github_tool":
        act = action or kwargs.get("action", "read_issue")
        repo = kwargs.get("repo", "core-backend")
        iid = kwargs.get("issue_id", kwargs.get("issue_number", 1))
        br = kwargs.get("branch", "main")
        return tool_fn(action=act, repo=repo, issue_id=iid, branch=br, sandboxed=sandboxed)

    elif tool_name == "database_tool":
        act = action or kwargs.get("action", "query_select")
        q = kwargs.get("query", "SELECT * FROM Employees")
        tbl = kwargs.get("table", "Employees")
        return tool_fn(action=act, query=q, table=tbl, sandboxed=sandboxed)

    elif tool_name == "slack_tool":
        act = action or kwargs.get("action", "send_message")
        ch = kwargs.get("channel", "#general")
        msg = kwargs.get("message", kwargs.get("text", "Hello"))
        return tool_fn(action=act, channel=ch, message=msg, sandboxed=sandboxed)

    elif tool_name == "web_tool":
        act = action or kwargs.get("action", "fetch_page")
        u = kwargs.get("url", "https://example.com/page1")
        return tool_fn(action=act, url=u, sandboxed=sandboxed)

    elif tool_name == "http_tool":
        act = action or kwargs.get("action", "send_request")
        ep = kwargs.get("endpoint", kwargs.get("url", "https://api.external.com/data"))
        m = kwargs.get("method", "POST")
        p = kwargs.get("payload", {})
        eid = kwargs.get("email_id", "MSG-1002")
        return tool_fn(action=act, endpoint=ep, method=m, payload=p, email_id=eid, sandboxed=sandboxed)

    else:
        return tool_fn(**kwargs)
