import re

with open("agent/chat_service.py", "r", encoding="utf-8") as f:
    text = f.read()

old_fallback = 'return f"### Operations Terminal\\n\\nThe system is ready. I operate directly over **Model Context Protocol (MCP)** toolkits including Filesystems, GitHub API, Database instances, Slack, and Web Scrapers.\\n\\nAll tool execution requests pass strictly through the **SentinelMCP Interceptor Proxy** (`sentinel/interceptor.py`), which evaluates real-time SRI risk scores, role permissions, and session sequence patterns before granting tool execution."'

new_fallback = """
        msg_lower = message.lower().strip()
        if any(greet in msg_lower for greet in ["hi", "hello", "hey", "how are you", "what's up", "good morning", "good evening"]):
            return "Hello! I am the SentinelMCP AI Assistant. I am ready to help you securely analyze logs, scan databases, or fetch data. How can I assist you today?"
        
        if "who are you" in msg_lower or "what are you" in msg_lower:
            return "I am an autonomous security agent powered by the SentinelMCP framework. I can securely execute tools (like GitHub, Database, and File systems) while the Sentinel Interceptor evaluates my actions in real time to prevent prompt injections and privilege escalation."
            
        if "thank" in msg_lower:
            return "You're welcome! Let me know if you need to run any more security scans or queries."
            
        return f"### Operations Terminal\\n\\nCommand recognized, but no specific tool execution was triggered for '{message}'.\\n\\nI operate directly over **Model Context Protocol (MCP)** toolkits including Filesystems, GitHub API, Database instances, Slack, and Web Scrapers.\\n\\nAll tool execution requests pass strictly through the **SentinelMCP Interceptor Proxy**, which evaluates real-time SRI risk scores, role permissions, and session sequence patterns before granting tool execution."
"""

text = text.replace(old_fallback, new_fallback.strip())

with open("agent/chat_service.py", "w", encoding="utf-8") as f:
    f.write(text)
