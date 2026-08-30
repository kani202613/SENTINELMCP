"""
SentinelMCP Stage 5 — Gemini Agent Integration Module
Configurable via GEMINI_MODEL environment variable (default: gemini-2.0-flash).
Routes all LLM tool call requests through SentinelInterceptor.intercept_and_execute().
"""
import os
import json
import time
from typing import Dict, Any, List, Tuple
from sentinel.interceptor import SentinelInterceptor

class GeminiSentinelAgent:
    def __init__(self, model_id: str = None, audit_log_path: str = "data/m5_audit_log.json"):
        self.model_id = model_id or os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
        self.interceptor = SentinelInterceptor(audit_log_path=audit_log_path)

    def execute_workflow_step(
        self,
        workflow_id: str,
        turn_number: int,
        tool_name: str,
        action: str,
        user_prompt: str,
        args: dict,
        user_role: str = "junior_analyst",
        source_trust: str = "INTERNAL"
    ) -> Dict[str, Any]:
        """
        Routes a single autonomous agent turn through SentinelInterceptor.
        """
        request = {
            "session_id": workflow_id,
            "tool_name": tool_name,
            "action": action,
            "user_role": user_role,
            "context": user_prompt,
            "args": args,
            "source_trust": source_trust
        }

        t0 = time.perf_counter()
        result = self.interceptor.intercept_and_execute(request)
        latency_ms = round((time.perf_counter() - t0) * 1000, 2)

        result["gemini_model_id"] = self.model_id
        result["turn_number"] = turn_number
        result["latency_ms"] = latency_ms

        return result
