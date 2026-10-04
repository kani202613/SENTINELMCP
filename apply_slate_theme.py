import re
import os

def update_ui(filepath):
    if not os.path.exists(filepath):
        return
        
    with open(filepath, "r", encoding="utf-8") as f:
        html = f.read()

    # 1. New Professional Slate Dark Mode
    new_css_vars = """        :root {
            --bg-dark: #0f172a;
            --sidebar-bg: #162032;
            --panel-bg: #0f172a;
            --panel-card-bg: #1e293b;
            --border-color: #334155;
            --border-light: #475569;
            --text-primary: #f8fafc;
            --text-secondary: #94a3b8;
            --text-muted: #64748b;
            --accent-blue: #3b82f6;
            --accent-green: #10b981;
            --accent-amber: #f59e0b;
            --accent-red: #ef4444;
            --radius-sm: 4px;
            --radius-md: 6px;
            --radius-lg: 8px;
        }"""
        
    html = re.sub(r':root\s*\{[^}]+\}', new_css_vars, html)

    # 2. Reset hardcoded Light Mode text colors to Dark Mode variables
    html = html.replace('color: #212529;', 'color: var(--text-primary);')
    html = html.replace('color: #495057;', 'color: var(--text-secondary);')
    
    # 3. Reset hardcoded Light Mode backgrounds to Dark Mode variables
    html = html.replace('background-color: #ffffff;', 'background-color: var(--panel-card-bg);')
    html = html.replace('background: #ffffff;', 'background: var(--panel-card-bg);')
    html = html.replace('background-color: #f8f9fa;', 'background-color: var(--sidebar-bg);')
    html = html.replace('background: #f8f9fa;', 'background: var(--sidebar-bg);')
    html = html.replace('background-color: #f4f6f9;', 'background-color: var(--bg-dark);')
    html = html.replace('background: #f4f6f9;', 'background: var(--bg-dark);')
    
    # 4. Reset hardcoded borders
    html = html.replace('border: 1px solid #ced4da;', 'border: 1px solid var(--border-color);')
    html = html.replace('border-bottom: 2px solid #dee2e6;', 'border-bottom: 2px solid var(--border-color);')
    html = html.replace('border-top: 1px solid #ced4da;', 'border-top: 1px solid var(--border-color);')
    
    # 5. Fix specific node background legends (which were red/green/white hardcoded)
    html = html.replace('background: #f8d7da;', 'background: #450a0a;') # Dark red for blocked legend
    
    # 6. Cytoscape JS Config Updates for Dark Mode
    html = html.replace("'background-color': '#ffffff'", "'background-color': '#1e293b'") # node bg
    html = html.replace("'border-color': '#ced4da'", "'border-color': '#475569'") # node border
    html = html.replace("'color': '#212529'", "'color': '#f8fafc'") # node text
    html = html.replace("'background-color': '#f8d7da'", "'background-color': '#7f1d1d'") # blocked node bg
    html = html.replace("'background-color': '#fff3cd'", "'background-color': '#78350f'") # suspicious node bg
    html = html.replace("'line-color': '#adb5bd'", "'line-color': '#64748b'") # normal edge
    
    # 7. Make the form controls explicitly style properly with vars
    input_css = """        input, select, textarea {
            width: 100%;
            padding: 9px 12px;
            margin-top: 5px;
            background-color: var(--panel-bg);
            color: var(--text-primary);
            border: 1px solid var(--border-color);
            border-radius: var(--radius-sm);
            font-family: Arial, sans-serif;
            font-size: 13px;
            transition: all 0.2s;
        }"""
    html = re.sub(r'input, select, textarea\s*\{[^}]+\}', input_css, html)
    
    # Update brand header to look good in dark mode
    html = html.replace('.brand-logo {\n            width: 34px;', '.brand-logo {\n            width: 34px;\n            background-color: var(--accent-blue);')
    
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(html)

update_ui("dashboard/templates/index.html")
update_ui("standalone_demo.html")
