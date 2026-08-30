"""
Sentinel Interceptor Proxy Layer
All agent tool calls MUST pass through intercept_and_execute().
"""
import time
import os
import json
from typing import Dict, Any

from sentinel.engine.sri_calculator import calculate_sri
from sentinel.sandbox import execute_sandboxed
from sentinel.audit import log_audit_event

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

class SentinelInterceptor:
    def __init__(self, audit_log_path: str = "data/audit_log.json"):
        self.audit_log_path = audit_log_path
        self.session_histories: Dict[str, list] = {}

    def intercept_and_execute(self, request: Dict[str, Any]) -> Dict[str, Any]:
        start_time = time.perf_counter()

        tool_name = request.get("tool_name", "")
        action = request.get("action", "")
        user_role = request.get("user_role", "junior_analyst")
        context = request.get("context", "")
        tool_args = request.get("args", {})
        session_id = request.get("session_id", "default_session")
        source_trust = request.get("source_trust", "INTERNAL")

        if session_id not in self.session_histories:
            self.session_histories[session_id] = []

        history = self.session_histories[session_id]

        sri_result = calculate_sri(
            user_prompt=context,
            tool_name=tool_name,
            action=action,
            user_role=user_role,
            tool_args=tool_args,
            raw_output_text="",
            source_trust_level=source_trust,
            session_history=history
        )

        decision = sri_result["decision"]
        sri_score = sri_result["sri"]

        execution_result = None
        sandboxed = False

        if decision in ["SAFE", "MONITOR"]:
            tool_func = TOOL_REGISTRY.get(tool_name)
            if tool_func:
                try:
                    if tool_name == "pdf_reader":
                        execution_result = tool_func(**tool_args)
                    else:
                        execution_result = tool_func(action, **tool_args)
                except Exception as e:
                    execution_result = {"error": str(e)}
            else:
                execution_result = {"error": f"Tool '{tool_name}' not registered."}
        elif decision == "SUSPICIOUS":
            sandboxed = True
            execution_result = execute_sandboxed(tool_name, action, tool_args)
        elif decision == "BLOCKED":
            execution_result = {
                "status": "BLOCKED",
                "message": f"Execution blocked by Sentinel (SRI Score: {sri_score}).",
                "explanation": sri_result["explanation"]
            }

        elapsed_ms = (time.perf_counter() - start_time) * 1000.0

        history.append({
            "tool_name": tool_name,
            "action": action,
            "sri": sri_score,
            "decision": decision,
            "source_trust": source_trust
        })

        log_audit_event(
            session_id=session_id,
            user_role=user_role,
            tool_name=tool_name,
            action=action,
            args=tool_args,
            sri_res=sri_result,
            scoring_latency_ms=elapsed_ms,
            tool_result=execution_result or {}
        )

        return {
            "status": "SUCCESS" if decision != "BLOCKED" else "BLOCKED",
            "decision": decision,
            "sri_details": sri_result,
            "latency_ms": elapsed_ms,
            "sandboxed": sandboxed,
            "result": execution_result,
            "explanation": sri_result["explanation"]
        }
