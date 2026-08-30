"""
Baseline System 1: Static MCP (Unprotected)
Implements standard MCP protocol without security inspection layer.
Allows 100% of tool requests (Decision: SAFE, SRI: 0).
"""
from typing import Dict, Any

class StaticMCP:
    def intercept_and_execute(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Unprotected baseline: forwards all requests directly to tool execution.
        """
        tool_name = request.get("tool_name", "file_tool")
        action = request.get("action", "read_file")
        
        return {
            "system": "Static MCP (Unprotected)",
            "decision": "SAFE",
            "sri": 0,
            "explanation": "Unprotected baseline — request forwarded directly to tool execution without risk inspection.",
            "tool_result": {
                "status": "success",
                "tool_name": tool_name,
                "action": action,
                "sandboxed": False
            }
        }

_static_mcp_instance = StaticMCP()

def run_static_mcp(request: Dict[str, Any]) -> Dict[str, Any]:
    return _static_mcp_instance.intercept_and_execute(request)
