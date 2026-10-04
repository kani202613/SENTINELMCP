import re

with open("dashboard/templates/index.html", "r", encoding="utf-8") as f:
    html = f.read()

# Replace modern dark mode with a simple academic/enterprise light mode
css_vars = """
        :root {
            --bg-dark: #f4f6f9;
            --sidebar-bg: #343a40;
            --panel-bg: #ffffff;
            --panel-card-bg: #ffffff;
            --border-color: #dee2e6;
            --border-light: #e9ecef;
            --text-primary: #212529;
            --text-secondary: #495057;
            --text-muted: #6c757d;
            --accent-blue: #007bff;
            --accent-green: #28a745;
            --accent-amber: #ffc107;
            --accent-red: #dc3545;
            --radius-sm: 2px;
            --radius-md: 3px;
            --radius-lg: 4px;
        }
"""
html = re.sub(r":root\s*{[^}]+}", css_vars, html)

# Change font to Arial
html = html.replace("font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;", "font-family: Arial, sans-serif;")
html = html.replace("font-family: 'JetBrains Mono', monospace;", "font-family: Consolas, monospace;")

# Remove Google Fonts
html = re.sub(r'<link rel="preconnect"[^>]+>\n\s*', '', html)
html = re.sub(r'<link href="https://fonts.googleapis.com[^>]+>\n\s*', '', html)

# Fix background rgba colors (glassmorphism looks AI generated)
html = re.sub(r"background: rgba\([^)]+\);", "background: #f8f9fa;", html)
html = re.sub(r"background-color: rgba\([^)]+\);", "background-color: #f8f9fa;", html)

# Dark text for light mode
html = html.replace("color: #fff;", "color: #212529;")
html = html.replace("color: #ffffff;", "color: #212529;")

# Specific fix for sidebar text (which is dark bg)
html = html.replace('.brand-name { font-size: 15px; font-weight: 800; letter-spacing: -0.3px; color: #212529; }', '.brand-name { font-size: 15px; font-weight: bold; color: #ffffff; }')
html = html.replace('.header-page-title { font-size: 17px; font-weight: 700; margin: 0; color: #212529; letter-spacing: -0.3px; }', '.header-page-title { font-size: 17px; font-weight: bold; margin: 0; color: #ffffff; }')

# Make borders solid instead of subtle
html = html.replace('border: 1px solid var(--border-color);', 'border: 1px solid #ced4da;')

with open("dashboard/templates/index.html", "w", encoding="utf-8") as f:
    f.write(html)
