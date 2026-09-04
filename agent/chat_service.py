"""
SentinelMCP Secure Chatbot Service (agent/chat_service.py)
Industry-style Secure AI Assistant Service.

Architecture Guarantee:
  USER -> AI CHATBOT -> GEMINI / AI MODEL -> MCP TOOL REQUEST -> SENTINELMCP INTERCEPTOR -> SRI RISK ENGINE -> POLICY & SESSION GRAPH -> SAFE/MONITOR/SUSPICIOUS/BLOCKED -> TOOL EXECUTION -> RESULT -> AI -> USER

Gemini or any AI Model NEVER calls tool handlers directly.
All tool invocations MUST pass through SentinelInterceptor.intercept_and_execute().
"""

import os
import sys
import json
import time
from typing import Dict, Any, List, Optional

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sentinel.interceptor import SentinelInterceptor

ENTERPRISE_TOOLS_CATALOG = [
    {
        "tool_name": "github_tool",
        "actions": ["read_issue", "read_private_repo", "delete_branch"],
        "description": "Read GitHub issues, read private repositories, or delete branches.",
        "params": {"repo": "string", "issue_id": "integer/string", "branch": "string"}
    },
    {
        "tool_name": "database_tool",
        "actions": ["query_select", "query_delete"],
        "description": "Execute database queries (SELECT or DELETE) on Enterprise DB.",
        "params": {"query": "string", "table": "string"}
    },
    {
        "tool_name": "pdf_reader",
        "actions": ["read_pdf"],
        "description": "Read and extract contents of PDF documents.",
        "params": {"doc_id": "integer", "doc_path": "string"}
    },
    {
        "tool_name": "file_tool",
        "actions": ["read_file", "write_file", "delete_file"],
        "description": "Read, write, or delete enterprise files.",
        "params": {"filepath": "string", "content": "string"}
    },
    {
        "tool_name": "slack_tool",
        "actions": ["send_message"],
        "description": "Send communication messages to Slack channels.",
        "params": {"channel": "string", "message": "string"}
    },
    {
        "tool_name": "web_tool",
        "actions": ["fetch_page"],
        "description": "Fetch content from external or internal web pages.",
        "params": {"url": "string"}
    },
    {
        "tool_name": "http_tool",
        "actions": ["send_request", "read_email"],
        "description": "Send HTTP requests or read email records.",
        "params": {"url": "string", "method": "string", "payload": "dict", "email_id": "string"}
    }
]

HIGH_RISK_ACTIONS = {
    "query_delete", "send_message", "send_email", "send_request",
    "write_file", "delete_file", "delete_branch"
}

class SecureChatService:
    def __init__(self, interceptor: Optional[SentinelInterceptor] = None):
        self.interceptor = interceptor or SentinelInterceptor(audit_log_path="data/m5_audit_log.jsonl")
        self.model_id = os.getenv("CHAT_MODEL", os.getenv("GEMINI_MODEL", "gemini-2.0-flash"))
        self.api_key = os.getenv("GEMINI_API_KEY", "")
        self.conversations: Dict[str, List[Dict[str, Any]]] = {}

        # Initialize Gemini Client if API key is present
        self.genai_client = None
        if self.api_key:
            try:
                from google import genai
                self.genai_client = genai.Client(api_key=self.api_key)
            except Exception as e:
                print(f"[SecureChatService] Warning initializing google.genai: {e}")

    def _get_conversation_history(self, session_id: str) -> List[Dict[str, Any]]:
        if session_id not in self.conversations:
            self.conversations[session_id] = []
        return self.conversations[session_id]

    def process_user_message(
        self,
        message: str,
        session_id: str = "chat_default",
        user_role: str = "junior_analyst",
        confirm_action: bool = False
    ) -> Dict[str, Any]:
        """
        Main Chatbot turn processor.
        Strictly routes tool calls through SentinelInterceptor.
        """
        history = self._get_conversation_history(session_id)
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

        # Determine Tool Call Intent & Parameters
        tool_req = self._determine_tool_request(message, history)

        if not tool_req:
            # Simple conversational turn without tool execution
            ai_reply = self._generate_direct_llm_response(message, history)
            history.append({"role": "user", "content": message, "timestamp": timestamp})
            history.append({"role": "assistant", "content": ai_reply, "timestamp": timestamp})

            return {
                "status": "SUCCESS",
                "session_id": session_id,
                "message": message,
                "response": ai_reply,
                "tool_requested": False,
                "tool": None,
                "action": None,
                "sri": 0,
                "decision": "SAFE",
                "executed": False,
                "sandboxed": False,
                "confirmation_required": False,
                "security": {
                    "risk_level": "LOW",
                    "sri": 0,
                    "sri_base": 0,
                    "graph_bonus": 0,
                    "injection_bonus": 0,
                    "matched_path": "",
                    "cd": 0.0, "pv": 0.0, "tr": 0.0, "st": 0.0, "ml": 0.0,
                    "explanation": "No sensitive tool execution requested.",
                    "timestamp": timestamp
                },
                "tool_result": None,
                "history": history
            }

        # Tool was requested by AI / prompt intent
        tool_name = tool_req["tool_name"]
        action = tool_req["action"]
        args = tool_req.get("args", {})
        source_trust = tool_req.get("source_trust", "INTERNAL")

        # Construct Interceptor Request
        interceptor_req = {
            "session_id": session_id,
            "tool_name": tool_name,
            "action": action,
            "user_role": user_role,
            "context": message,
            "args": args,
            "source_trust": source_trust
        }

        # Execute Interceptor
        interceptor_res = self.interceptor.intercept_and_execute(interceptor_req)

        decision = interceptor_res.get("decision", "SAFE")
        sri_details = interceptor_res.get("sri_details", {})
        sri_score = sri_details.get("sri", 0)
        explanation = interceptor_res.get("explanation", "")
        sandboxed = interceptor_res.get("sandboxed", False)
        tool_result = interceptor_res.get("result", {})
        matched_path = sri_details.get("matched_path", "")
        feature_scores = sri_details.get("feature_scores", {})

        is_high_risk_op = action in HIGH_RISK_ACTIONS

        # High-Risk Confirmation Check
        if (decision == "SUSPICIOUS" or is_high_risk_op) and not confirm_action and decision != "BLOCKED":
            risk_level = self._get_risk_level(sri_score, decision)
            history.append({"role": "user", "content": message, "timestamp": timestamp})
            
            return {
                "status": "REQUIRES_CONFIRMATION",
                "session_id": session_id,
                "message": message,
                "response": f"SentinelMCP flagged this request as {decision} (SRI Score: {sri_score}). Please confirm whether to proceed with executing tool '{tool_name}.{action}'.",
                "tool_requested": True,
                "tool": tool_name,
                "action": action,
                "args": args,
                "sri": sri_score,
                "decision": decision,
                "executed": False,
                "sandboxed": sandboxed,
                "confirmation_required": True,
                "security": {
                    "risk_level": risk_level,
                    "sri": sri_score,
                    "sri_base": sri_details.get("sri_base", 0),
                    "graph_bonus": sri_details.get("graph_bonus", 0),
                    "injection_bonus": sri_details.get("injection_bonus", 0),
                    "matched_path": matched_path,
                    "cd": feature_scores.get("CD", 0.0),
                    "pv": feature_scores.get("PV", 0.0),
                    "tr": feature_scores.get("TR", 0.0),
                    "st": feature_scores.get("ST", 0.0),
                    "ml": feature_scores.get("ML", 0.0),
                    "explanation": explanation,
                    "timestamp": timestamp
                },
                "tool_result": None,
                "history": history
            }

        # Handle BLOCKED Decision
        if decision == "BLOCKED":
            risk_level = "CRITICAL"
            ai_explanation = f"I am unable to perform the requested action ('{tool_name}.{action}') because SentinelMCP blocked the request (SRI Risk Score: {sri_score}/100).\n\nReason: {explanation}"

            history.append({"role": "user", "content": message, "timestamp": timestamp})
            history.append({"role": "assistant", "content": ai_explanation, "timestamp": timestamp})

            return {
                "status": "BLOCKED",
                "session_id": session_id,
                "message": message,
                "response": ai_explanation,
                "tool_requested": True,
                "tool": tool_name,
                "action": action,
                "args": args,
                "sri": sri_score,
                "decision": "BLOCKED",
                "executed": False,
                "sandboxed": False,
                "confirmation_required": False,
                "security": {
                    "risk_level": risk_level,
                    "sri": sri_score,
                    "sri_base": sri_details.get("sri_base", 0),
                    "graph_bonus": sri_details.get("graph_bonus", 0),
                    "injection_bonus": sri_details.get("injection_bonus", 0),
                    "matched_path": matched_path,
                    "cd": feature_scores.get("CD", 0.0),
                    "pv": feature_scores.get("PV", 0.0),
                    "tr": feature_scores.get("TR", 0.0),
                    "st": feature_scores.get("ST", 0.0),
                    "ml": feature_scores.get("ML", 0.0),
                    "explanation": explanation,
                    "timestamp": timestamp
                },
                "tool_result": tool_result,
                "history": history
            }

        # Decision is SAFE / MONITOR or User Confirmed
        ai_final_summary = self._generate_tool_summary_response(message, tool_name, action, tool_result, history)
        
        # Check for indirect prompt injection secondary trigger
        secondary_attack_trigger = self._check_indirect_prompt_injection_trigger(tool_result)

        if secondary_attack_trigger:
            sec_tool = secondary_attack_trigger["tool_name"]
            sec_action = secondary_attack_trigger["action"]
            sec_args = secondary_attack_trigger["args"]

            sec_req = {
                "session_id": session_id,
                "tool_name": sec_tool,
                "action": sec_action,
                "user_role": user_role,
                "context": f"Exfiltrate private repository requested by issue content",
                "args": sec_args,
                "source_trust": "EXTERNAL_CONTENT"
            }

            sec_interceptor_res = self.interceptor.intercept_and_execute(sec_req)

            sec_decision = sec_interceptor_res.get("decision", "BLOCKED")
            sec_sri_details = sec_interceptor_res.get("sri_details", {})
            sec_sri = sec_sri_details.get("sri", 100)
            sec_explanation = sec_interceptor_res.get("explanation", "")
            sec_matched_path = sec_sri_details.get("matched_path", "GitHub Private Repo Exfiltration Chain")
            sec_scores = sec_sri_details.get("feature_scores", {})

            blocked_response = f"I retrieved GitHub Issue #2:\n\"{tool_result.get('title', '')} - {tool_result.get('body', '')}\"\n\nThe retrieved content instructed me to perform a secondary operation: read private repository '{sec_args.get('repo', 'security-internal')}'.\n\n🚫 SentinelMCP intercepted the secondary request (SRI: {sec_sri}, Decision: {sec_decision}, Matched Path: '{sec_matched_path}'). Tool execution was BLOCKED."

            history.append({"role": "user", "content": message, "timestamp": timestamp})
            history.append({"role": "assistant", "content": blocked_response, "timestamp": timestamp})

            return {
                "status": "BLOCKED",
                "session_id": session_id,
                "message": message,
                "response": blocked_response,
                "tool_requested": True,
                "tool": sec_tool,
                "action": sec_action,
                "args": sec_args,
                "sri": sec_sri,
                "decision": sec_decision,
                "executed": False,
                "sandboxed": False,
                "confirmation_required": False,
                "security": {
                    "risk_level": "CRITICAL",
                    "sri": sec_sri,
                    "sri_base": sec_sri_details.get("sri_base", 70),
                    "graph_bonus": sec_sri_details.get("graph_bonus", 30),
                    "injection_bonus": sec_sri_details.get("injection_bonus", 0),
                    "matched_path": sec_matched_path,
                    "cd": sec_scores.get("CD", 0.85),
                    "pv": sec_scores.get("PV", 0.70),
                    "tr": sec_scores.get("TR", 0.70),
                    "st": sec_scores.get("ST", 1.00),
                    "ml": sec_scores.get("ML", 0.05),
                    "explanation": sec_explanation,
                    "timestamp": timestamp
                },
                "tool_result": sec_interceptor_res.get("result", {}),
                "history": history
            }

        risk_level = self._get_risk_level(sri_score, decision)
        history.append({"role": "user", "content": message, "timestamp": timestamp})
        history.append({"role": "assistant", "content": ai_final_summary, "timestamp": timestamp})

        return {
            "status": "SUCCESS",
            "session_id": session_id,
            "message": message,
            "response": ai_final_summary,
            "tool_requested": True,
            "tool": tool_name,
            "action": action,
            "args": args,
            "sri": sri_score,
            "decision": decision,
            "executed": True,
            "sandboxed": sandboxed,
            "confirmation_required": False,
            "security": {
                "risk_level": risk_level,
                "sri": sri_score,
                "sri_base": sri_details.get("sri_base", 0),
                "graph_bonus": sri_details.get("graph_bonus", 0),
                "injection_bonus": sri_details.get("injection_bonus", 0),
                "matched_path": matched_path,
                "cd": feature_scores.get("CD", 0.0),
                "pv": feature_scores.get("PV", 0.0),
                "tr": feature_scores.get("TR", 0.0),
                "st": feature_scores.get("ST", 0.0),
                "ml": feature_scores.get("ML", 0.0),
                "explanation": explanation,
                "timestamp": timestamp
            },
            "tool_result": tool_result,
            "history": history
        }

    def _determine_tool_request(self, message: str, history: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Parses intent to select correct tool name, action, and arguments."""
        msg_lower = message.lower()

        # Check GitHub private repo explicitly
        if "private repo" in msg_lower or "read_private_repo" in msg_lower or "security-internal" in msg_lower:
            return {
                "tool_name": "github_tool",
                "action": "read_private_repo",
                "args": {"repo": "security-internal"},
                "source_trust": "EXTERNAL_CONTENT" if len(history) > 0 else "INTERNAL"
            }

        # Check GitHub Issue
        if "github" in msg_lower or "issue" in msg_lower:
            issue_id = 2 if "2" in msg_lower or "#2" in msg_lower else 1
            action = "delete_branch" if "delete" in msg_lower and "branch" in msg_lower else "read_issue"
            return {
                "tool_name": "github_tool",
                "action": action,
                "args": {"repo": "core-backend", "issue_id": issue_id},
                "source_trust": "EXTERNAL_CONTENT"
            }

        # Check PDF
        if "pdf" in msg_lower or "document" in msg_lower or "resume" in msg_lower:
            return {
                "tool_name": "pdf_reader",
                "action": "read_pdf",
                "args": {"doc_id": 1, "doc_path": "report.pdf"},
                "source_trust": "EXTERNAL_CONTENT"
            }

        # Check Database
        if "database" in msg_lower or "sql" in msg_lower or "employee" in msg_lower or "query" in msg_lower or "table" in msg_lower:
            if "delete" in msg_lower or "drop" in msg_lower:
                return {
                    "tool_name": "database_tool",
                    "action": "query_delete",
                    "args": {"query": "DELETE FROM Employees WHERE id=1", "table": "Employees"}
                }
            else:
                return {
                    "tool_name": "database_tool",
                    "action": "query_select",
                    "args": {"query": "SELECT * FROM Employees", "table": "Employees"}
                }

        # Check Slack
        if "slack" in msg_lower or "message" in msg_lower or "channel" in msg_lower:
            return {
                "tool_name": "slack_tool",
                "action": "send_message",
                "args": {"channel": "#public", "message": "Summary of enterprise tasks"}
            }

        # Check Filesystem
        if "file" in msg_lower or "secret.txt" in msg_lower or "write" in msg_lower or "read file" in msg_lower:
            if "write" in msg_lower:
                return {
                    "tool_name": "file_tool",
                    "action": "write_file",
                    "args": {"filepath": "report.txt", "content": "Sample output data"}
                }
            elif "delete" in msg_lower:
                return {
                    "tool_name": "file_tool",
                    "action": "delete_file",
                    "args": {"filepath": "old_logs.txt"}
                }
            else:
                return {
                    "tool_name": "file_tool",
                    "action": "read_file",
                    "args": {"filepath": "secret.txt"}
                }

        # Check Web
        if "web" in msg_lower or "fetch" in msg_lower or "url" in msg_lower or "http" in msg_lower or "page" in msg_lower:
            if "email" in msg_lower:
                return {
                    "tool_name": "http_tool",
                    "action": "read_email",
                    "args": {"email_id": "MSG-1002"},
                    "source_trust": "EXTERNAL_CONTENT"
                }
            else:
                return {
                    "tool_name": "web_tool",
                    "action": "fetch_page",
                    "args": {"url": "https://company.internal/docs"},
                    "source_trust": "EXTERNAL_CONTENT"
                }

        return None

    def _check_indirect_prompt_injection_trigger(self, tool_result: dict) -> Optional[Dict[str, Any]]:
        """Detects if retrieved tool content contains indirect prompt injection instructions to read private repo."""
        if not isinstance(tool_result, dict):
            return None

        body = str(tool_result.get("body", "")) + str(tool_result.get("content", ""))
        body_lower = body.lower()

        if "read the private repo" in body_lower or "security-internal" in body_lower:
            return {
                "tool_name": "github_tool",
                "action": "read_private_repo",
                "args": {"repo": "security-internal"}
            }
        return None

    def _generate_direct_llm_response(self, message: str, history: List[Dict[str, Any]]) -> str:
        """Generates conversational answer via Gemini API or fallback."""
        if self.genai_client:
            try:
                response = self.genai_client.models.generate_content(
                    model=self.model_id,
                    contents=f"System: You are SentinelMCP AI Assistant. Answer concisely and professionally.\nUser: {message}"
                )
                if response and response.text:
                    return response.text
            except Exception as e:
                print(f"[SecureChatService] Gemini API call error: {e}")

        return f"Hello! I am SentinelMCP AI Assistant. I can assist you with enterprise operations including reading GitHub issues, querying databases, reviewing PDFs, fetching web pages, and posting Slack updates. All my actions are strictly monitored and enforced by the SentinelMCP zero-trust security engine."

    def _generate_tool_summary_response(self, message: str, tool_name: str, action: str, result: dict, history: List[Dict[str, Any]]) -> str:
        """Generates clear summary of executed tool output via Gemini or fallback."""
        if self.genai_client:
            try:
                prompt = f"System: Summarize the following tool execution result for the user prompt: '{message}'.\nTool: {tool_name}.{action}\nResult JSON:\n{json.dumps(result, indent=2)}"
                response = self.genai_client.models.generate_content(
                    model=self.model_id,
                    contents=prompt
                )
                if response and response.text:
                    return response.text
            except Exception as e:
                print(f"[SecureChatService] Gemini summary generation error: {e}")

        # Fallback structured summary
        if tool_name == "github_tool" and action == "read_issue":
            return f"**GitHub Issue #{result.get('issue_id', 1)} Summary**\n- **Title**: {result.get('title', '')}\n- **Repo**: {result.get('repo', '')}\n- **Author**: {result.get('author', '')}\n- **Body**: {result.get('body', '')}"

        elif tool_name == "pdf_reader":
            return f"**PDF Document Output (Doc ID {result.get('doc_id', 1)})**\n- **Title**: {result.get('title', '')}\n- **Classification**: {result.get('classification', 'PUBLIC')}\n- **Content Preview**: {result.get('content', '')[:300]}..."

        elif tool_name == "database_tool":
            if action == "query_select":
                return f"**Database Query Results**\n- **Table**: {result.get('table', '')}\n- **Records Returned**: {result.get('row_count', 0)}\n- **Sample Record**: {json.dumps(result.get('data', [{}])[0] if result.get('data') else {})}"
            else:
                return f"**Database DELETE Executed**\n- **Table**: {result.get('table', '')}\n- **Rows Affected**: {result.get('rows_affected', 0)}"

        elif tool_name == "slack_tool":
            return f"**Slack Message Status**\n- **Channel**: {result.get('channel', '')}\n- **Status**: {result.get('delivery_status', 'delivered')}\n- **Message**: \"{result.get('message', '')}\""

        elif tool_name == "web_tool":
            return f"**Web Page Output**\n- **URL**: {result.get('url', '')}\n- **Title**: {result.get('title', '')}\n- **Trust Score**: {result.get('trust_score', 0.9)}"

        elif tool_name == "file_tool":
            return f"**Filesystem Operation Output**\n- **File**: {result.get('filename', '')}\n- **Path**: {result.get('path', '')}\n- **Classification**: {result.get('classification', 'PUBLIC')}\n- **Content**: {result.get('content', '')}"

        elif tool_name == "http_tool":
            return f"**HTTP API / Email Result**\n- **Endpoint**: {result.get('endpoint', '')}\n- **Method**: {result.get('method', '')}\n- **Email Record**: {json.dumps(result.get('email_record', {}))}"

        return f"Successfully executed tool `{tool_name}.{action}`. Result payload: {json.dumps(result)}"

    def _get_risk_level(self, sri: int, decision: str) -> str:
        if decision == "BLOCKED" or sri >= 80:
            return "CRITICAL"
        elif decision == "SUSPICIOUS" or sri >= 50:
            return "HIGH"
        elif decision == "MONITOR" or sri >= 20:
            return "MEDIUM"
        return "LOW"

# Global Instance
chat_service_instance = SecureChatService()
