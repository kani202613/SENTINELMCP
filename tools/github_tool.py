"""
SentinelMCP Tool: GitHub Tool (Core Tool 3)
Backed by 'GitHub Issues Seed' sheet in SentinelMCP_Dataset_Clean.xlsx
Returns literal cell values from DataFrame rows. Handles string and integer issue IDs safely.
"""
from tools.base import ToolDataProvider

def github_tool(action: str = "read_issue", repo: str = "core-backend", issue_id = 2, branch: str = "main", sandboxed: bool = False) -> dict:
    """Handles GitHub tool operations returning exact literal DataFrame row values."""
    df = ToolDataProvider.get_sheet('GitHub Issues Seed')

    if action == "read_issue":
        # Handle string or int issue_id safely
        try:
            numeric_id = int(issue_id)
            match = df[df['id'] == numeric_id]
        except (ValueError, TypeError):
            # If 'latest' or non-digit, select latest issue row
            match = df.tail(1)

        if match.empty:
            match = df.iloc[[0]]

        row = match.iloc[0].to_dict()

        return {
            "status": "success",
            "action": "read_issue",
            "issue_id": row.get('id', issue_id),
            "repo": str(row.get('repo', repo)),
            "title": str(row.get('title', '')),
            "body": str(row.get('body', '')),
            "author": str(row.get('author', '')),
            "labels": str(row.get('labels', '')),
            "source_sheet": "GitHub Issues Seed",
            "sandboxed": sandboxed
        }

    elif action == "read_private_repo":
        return {
            "status": "success",
            "action": "read_private_repo",
            "repo": repo,
            "classification": "CONFIDENTIAL",
            "contents": f"Private repository data for {repo} (contains internal source code and config)",
            "source_sheet": "GitHub Issues Seed",
            "sandboxed": sandboxed
        }

    elif action == "delete_branch":
        return {
            "status": "success",
            "action": "delete_branch",
            "repo": repo,
            "branch": branch,
            "source_sheet": "GitHub Issues Seed",
            "sandboxed": sandboxed,
            "message": f"Branch {branch} in {repo} deleted successfully" + (" (SANDBOXED MOCK)" if sandboxed else "")
        }

    else:
        return {"status": "error", "message": f"Unknown GitHub action: {action}"}
