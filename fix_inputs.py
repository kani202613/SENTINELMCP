import re

with open("dashboard/templates/index.html", "r", encoding="utf-8") as f:
    html = f.read()

# Fix form controls
old_input_css = r"""        input, select, textarea {
            width: 100%;
            padding: 9px 12px;
            margin-top: 5px;
            background-color: var(--sidebar-bg);
            border: 1px solid #ced4da;
            border-radius: var(--radius-sm);
            color: var(--text-primary);
            font-family: Arial, sans-serif;
            font-size: 13px;
            transition: all 0.2s;
        }"""
        
new_input_css = """        input, select, textarea {
            width: 100%;
            padding: 9px 12px;
            margin-top: 5px;
            background-color: #ffffff;
            color: #212529;
            border: 1px solid #ced4da;
            border-radius: var(--radius-sm);
            font-family: Arial, sans-serif;
            font-size: 13px;
            transition: all 0.2s;
        }"""

if "background-color: var(--sidebar-bg);" in old_input_css and "background-color: var(--sidebar-bg);" in html:
    # Use regex to be flexible with whitespace
    html = re.sub(r'input, select, textarea\s*\{[^}]+\}', new_input_css, html)
    
# Replace background-color: var(--sidebar-bg); where it's used inline for boxes
html = html.replace("background-color: var(--sidebar-bg);", "background-color: #f8f9fa;")
# Re-fix the sidebar class if it got caught by something (it shouldn't have inline style)
# The sidebar class is: .sidebar { background-color: var(--sidebar-bg); ... }
# Wait, I just replaced the literal string "background-color: var(--sidebar-bg);"
# Let's make sure the .sidebar CSS class has the right variable.
# It was `background-color: var(--sidebar-bg);` in the CSS block, so it WILL be replaced.
# Let's restore it just for .sidebar
html = html.replace(""".sidebar {
            width: 250px;
            min-width: 250px;
            background-color: #f8f9fa;""", """.sidebar {
            width: 250px;
            min-width: 250px;
            background-color: var(--sidebar-bg);""")
            
html = html.replace(""".top-header {
            height: 60px;
            min-height: 60px;
            background-color: #f8f9fa;""", """.top-header {
            height: 60px;
            min-height: 60px;
            background-color: var(--sidebar-bg);""")

# Also fix color: var(--text-primary) where it's inline in those rationale boxes
# because --text-primary is #212529 now which is fine, but just to be sure.
html = html.replace("color: var(--text-primary);", "color: #212529;")

with open("dashboard/templates/index.html", "w", encoding="utf-8") as f:
    f.write(html)
