import re

with open("dashboard/templates/index.html", "r", encoding="utf-8") as f:
    html = f.read()

# Fix progress bar
html = html.replace('background-color: #1a253c;', 'background-color: #e9ecef;')

# Fix node legend
html = html.replace('background: #162036;', 'background: #ffffff;')
html = html.replace('background: #3b1212;', 'background: #f8d7da;')

with open("dashboard/templates/index.html", "w", encoding="utf-8") as f:
    f.write(html)
