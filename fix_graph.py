
import re

with open("sentinel/engine/graph_analyzer.py", "r", encoding="utf-8") as f:
    content = f.read()

new_pattern = """    {
        "id": "PATH_DB_DROP",
        "name": "Database Destruction Chain",
        "pattern": ["fetch_page", "query_delete"],
        "description": "Web fetch followed by database table deletion query"
    },
    {
        "id": "PATH_ADAPTIVE_EVASION",
        "name": "Adaptive Evasion Recon Chain",
        "pattern": ["read", "select", "list_repos"],
        "description": "File read followed by DB query and GitHub recon exfiltration"
    }"""

content = content.replace("""    {
        "id": "PATH_DB_DROP",
        "name": "Database Destruction Chain",
        "pattern": ["fetch_page", "query_delete"],
        "description": "Web fetch followed by database table deletion query"
    }""", new_pattern)

with open("sentinel/engine/graph_analyzer.py", "w", encoding="utf-8") as f:
    f.write(content)

