import re

with open("dashboard/templates/index.html", "r", encoding="utf-8") as f:
    html = f.read()

# Fix cy canvas background
html = html.replace('background-color: #0b101c;', 'background-color: #f8f9fa;')

# Fix node styles in JS
html = html.replace("'background-color': '#162036'", "'background-color': '#ffffff', 'border-width': 2, 'border-color': '#ced4da', 'color': '#212529'")
html = html.replace("'background-color': '#3b1212'", "'background-color': '#f8d7da'")
html = html.replace("'border-color': '#ef4444'", "'border-color': '#dc3545'")
html = html.replace("'background-color': '#3b2812'", "'background-color': '#fff3cd'")
html = html.replace("'border-color': '#f59e0b'", "'border-color': '#ffc107'")
html = html.replace("'line-color': '#64748b'", "'line-color': '#adb5bd'")

# Fix "Awaiting input" badge background that might be dark
html = html.replace('background: var(--sidebar-bg); border-top: 1px solid #ced4da; display: flex;', 'background: #f4f6f9; border-top: 1px solid #ced4da; display: flex;')

with open("dashboard/templates/index.html", "w", encoding="utf-8") as f:
    f.write(html)
