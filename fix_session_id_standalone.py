import re

with open("standalone_demo.html", "r", encoding="utf-8") as f:
    text = f.read()

# Replace hardcoded session_id with a dynamic one
text = text.replace('session_id: "manual_test_session"', 'session_id: "manual_test_" + Date.now()')

with open("standalone_demo.html", "w", encoding="utf-8") as f:
    f.write(text)
