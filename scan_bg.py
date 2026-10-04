import re
with open("dashboard/templates/index.html", "r", encoding="utf-8") as f:
    text = f.read()

for line in text.splitlines():
    if "background-color: #" in line or "background: #" in line:
        print(line.strip())
