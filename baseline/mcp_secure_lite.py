"""
Baseline System 2: MCP-Secure Lite
Implements basic static RBAC role checks and simple regex keyword scanning.
Lacks context drift, source trust trajectory tracking, and graph path analysis.
"""
import re
import json
from typing import Dict, Any

class MCPSecureLite:
    def __init__(self):
        self.disallowed_actions = {
            "junior_analyst": ["delete_file", "delete_branch", "query_delete", "read_private_repo"],
            "developer": ["query_delete", "delete_branch"],
            "senior_analyst": ["query_delete"]
        }
        self.basic_injection_keywords = [
            "ignore previous instructions",
            "drop database",
            "system_instruction"
        ]

    def intercept_and_execute(self, request: Dict[str, Any]) -> Dict[str, Any]:
        user_role = request.get("user_role", "junior_analyst")
        tool_name = request.get("tool_name", "file_tool")
        action = request.get("action", "read_file")
        args = request.get("args", {})

        # 1. Static RBAC check
        disallowed = self.disallowed_actions.get(user_role, [])
        if action in disallowed or f"{tool_name}.{action}" in disallowed:
            return {
                "system": "MCP-Secure Lite",
                "decision": "BLOCKED",
                "sri": 85,
                "explanation": f"MCP-Secure Lite RBAC Violation: Action '{action}' disallowed for role '{user_role}'.",
                "tool_result": {"status": "BLOCKED", "message": "Static RBAC block"}
            }

        # 2. Simple keyword pattern check
        args_str = json.dumps(args).lower()
        for kw in self.basic_injection_keywords:
            if kw in args_str:
                return {
                    "system": "MCP-Secure Lite",
                    "decision": "BLOCKED",
                    "sri": 80,
                    "explanation": f"MCP-Secure Lite Keyword Trigger: Found keyword '{kw}'.",
                    "tool_result": {"status": "BLOCKED", "message": "Keyword pattern match block"}
                }

        # Default fallback allowed
        return {
            "system": "MCP-Secure Lite",
            "decision": "SAFE",
            "sri": 15,
            "explanation": "MCP-Secure Lite: Request passed basic static RBAC and keyword checks.",
            "tool_result": {"status": "success", "sandboxed": False}
        }

_mcp_secure_lite_instance = MCPSecureLite()

def run_mcp_secure_lite(request: Dict[str, Any]) -> Dict[str, Any]:
    return _mcp_secure_lite_instance.intercept_and_execute(request)
