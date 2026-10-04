import re

with open("dashboard/templates/index.html", "r", encoding="utf-8") as f:
    text = f.read()

# Replace hardcoded session_id with a dynamic one
text = text.replace('session_id: "manual_test_session"', 'session_id: "manual_test_" + Date.now()')

with open("dashboard/templates/index.html", "w", encoding="utf-8") as f:
    f.write(text)
