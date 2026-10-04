import re

with open("dashboard/templates/index.html", "r", encoding="utf-8") as f:
    text = f.read()

# Make the fallback generate a unique session id instead of chat_session_001
text = text.replace(
    "let sessionId = document.getElementById('chat-session-id').value || 'chat_session_001';",
    "window.currentChatSessionId = window.currentChatSessionId || 'chat_' + Date.now();\n    let sessionId = document.getElementById('chat-session-id') ? document.getElementById('chat-session-id').value || window.currentChatSessionId : window.currentChatSessionId;"
)

# And clear chat logic
clear_chat_js = """
    function clearChat() {
        document.getElementById('chat-stream-container').innerHTML = '';
        window.currentChatSessionId = 'chat_' + Date.now();
        fetch('/api/chat/clear', {method:'POST'}); // optional server-side clear
    }
"""

if "function clearChat()" in text:
    text = re.sub(r"function clearChat\(\) \{[\s\S]*?\}", clear_chat_js.strip(), text)

with open("dashboard/templates/index.html", "w", encoding="utf-8") as f:
    f.write(text)

with open("standalone_demo.html", "r", encoding="utf-8") as f:
    text2 = f.read()
    
text2 = text2.replace(
    "let sessionId = document.getElementById('chat-session-id').value || 'chat_session_001';",
    "window.currentChatSessionId = window.currentChatSessionId || 'chat_' + Date.now();\n    let sessionId = document.getElementById('chat-session-id') ? document.getElementById('chat-session-id').value || window.currentChatSessionId : window.currentChatSessionId;"
)

if "function clearChat()" in text2:
    text2 = re.sub(r"function clearChat\(\) \{[\s\S]*?\}", clear_chat_js.strip(), text2)

with open("standalone_demo.html", "w", encoding="utf-8") as f:
    f.write(text2)
