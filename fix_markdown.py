import re

with open("dashboard/templates/index.html", "r", encoding="utf-8") as f:
    html = f.read()

# 1. Inject marked.js CDN
if "marked.min.js" not in html:
    html = html.replace("<!-- Google Font Inter -->", "<script src=\"https://cdn.jsdelivr.net/npm/marked/marked.min.js\"></script>\n    <!-- Google Font Inter -->")

# 2. Inject CSS rules for #chat-stream-container
css_rules = """
        /* CHAT MARKDOWN STYLES */
        #chat-stream-container h3 { font-size: 14px; font-weight: 800; color: #fff; margin: 10px 0 4px 0; border-bottom: 1px solid var(--border-color); padding-bottom: 4px; }
        #chat-stream-container h2 { font-size: 15px; font-weight: 800; color: #fff; margin: 12px 0 6px 0; }
        #chat-stream-container strong { color: #fff; }
        #chat-stream-container code:not(pre code) { background: var(--sidebar-bg); padding: 2px 6px; border-radius: 4px; color: var(--accent-blue); border: 1px solid var(--border-color); font-family: 'JetBrains Mono', monospace; font-size: 11px; }
        #chat-stream-container pre { background: var(--sidebar-bg); padding: 10px; border-radius: 6px; border: 1px solid var(--border-color); overflow-x: auto; color: var(--text-primary); font-family: 'JetBrains Mono', monospace; font-size: 11px; margin: 6px 0; }
        #chat-stream-container blockquote { border-left: 2px solid var(--border-color); padding-left: 10px; margin: 6px 0; color: var(--text-secondary); font-style: italic; }
        #chat-stream-container ul { margin: 6px 0; padding-left: 20px; }
        #chat-stream-container p { margin: 6px 0; }
        #chat-stream-container table { margin: 10px 0; border: 1px solid var(--border-color); border-radius: 4px; overflow: hidden; width: 100%; border-collapse: collapse; }
        #chat-stream-container th { background-color: var(--panel-card-bg); color: var(--text-muted); font-weight: 700; text-transform: uppercase; font-size: 10px; padding: 8px 12px; border-bottom: 1px solid var(--border-color); text-align: left; }
        #chat-stream-container td { padding: 8px 12px; border-bottom: 1px solid var(--border-color); color: var(--text-primary); }
"""
if "/* CHAT MARKDOWN STYLES */" not in html:
    html = html.replace("/* CYTOSCAPE CANVAS */", css_rules + "\n        /* CYTOSCAPE CANVAS */")

new_func = """    function formatMarkdownResponse(text) {
        if (typeof marked !== "undefined") {
            return marked.parse(text);
        }
        return escapeHtml(text);
    }"""

html = re.sub(r"function formatMarkdownResponse\(text\) \{[\s\S]*?return str;\s*\}", new_func, html)

with open("dashboard/templates/index.html", "w", encoding="utf-8") as f:
    f.write(html)
