import re

with open("agent/chat_service.py", "r", encoding="utf-8") as f:
    text = f.read()

# We will modify process_user_message to append the security thinking to the response.
old_str = 'ai_reply = self._generate_tool_summary_response(message, tool_name, action, tool_result, history, attachment)'

new_str = """
            # Generate the standard summary
            base_reply = self._generate_tool_summary_response(message, tool_name, action, tool_result, history, attachment)
            
            # Prepend the "SentinelMCP Thinking" to show off the project novelty
            thinking_block = (
                f"### 🛡️ SentinelMCP Zero-Trust Analysis\\n"
                f"Before executing this action, my proxy engine evaluated the request:\\n"
                f"- **Context Drift (CD)**: `{feature_scores.get('CD', 0.0)}`\\n"
                f"- **Policy Violation (PV)**: `{feature_scores.get('PV', 0.0)}`\\n"
                f"- **Transition Risk (TR)**: `{feature_scores.get('TR', 0.0)}`\\n"
                f"- **Source Trust (ST)**: `{feature_scores.get('ST', 0.0)}`\\n"
                f"- **ML Score**: `{feature_scores.get('ML', 0.0)}`\\n"
            )
            if matched_path:
                thinking_block += f"- **Graph Analyzer**: ⚠️ Detected Path: `{matched_path}`\\n"
            
            thinking_block += f"\\n**Final Decision**: `{decision}` (SRI: {sri_score})\\n---\\n\\n"
            
            ai_reply = thinking_block + base_reply
"""

text = text.replace(old_str, new_str.strip())

with open("agent/chat_service.py", "w", encoding="utf-8") as f:
    f.write(text)
