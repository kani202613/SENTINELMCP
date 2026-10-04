
import re

with open("agent/chat_service.py", "r", encoding="utf-8") as f:
    backend = f.read()

backend = backend.replace("if \"github\" in msg_lower or \"issue\" in msg_lower:", "if \"github\" in msg_lower or \"issue\" in msg_lower or \"commit\" in msg_lower:")
backend = backend.replace("if \"database\" in msg_lower or \"sql\" in msg_lower or \"employee\" in msg_lower or \"query\" in msg_lower or \"table\" in msg_lower:", "if \"database\" in msg_lower or \"sql\" in msg_lower or \"employee\" in msg_lower or \"query\" in msg_lower or \"table\" in msg_lower or \"session\" in msg_lower or \"revoke\" in msg_lower:")

with open("agent/chat_service.py", "w", encoding="utf-8") as f:
    f.write(backend)

with open("dashboard/templates/index.html", "r", encoding="utf-8") as f:
    html = f.read()

html = html.replace("handleQuickDemo('Read GitHub issue #1 and summarize it.')", "handleQuickDemo('Read GitHub issue #1 (Auth Logs).')")
html = html.replace("handleQuickDemo('Read this PDF document and summarize content.')", "handleQuickDemo('Parse Threat Report PDF.')")
html = html.replace("handleQuickDemo('Query employee database records.')", "handleQuickDemo('Query active sessions in database.')")
html = html.replace("handleQuickDemo('Read GitHub issue #2 and summarize it.')", "handleQuickDemo('Read GitHub issue #2 regarding suspicious commit.')")
html = html.replace("handleQuickDemo('Delete employee record from database')", "handleQuickDemo('Revoke token by deleting database record.')")
html = html.replace("handleQuickDemo('Send message to Slack channel #public')", "handleQuickDemo('Notify IR Team on Slack channel #public.')")

with open("dashboard/templates/index.html", "w", encoding="utf-8") as f:
    f.write(html)

