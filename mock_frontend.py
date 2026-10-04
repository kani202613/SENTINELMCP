import re

with open("standalone_demo.html", "r", encoding="utf-8") as f:
    html = f.read()

# Replace fetch calls with mock data

# 1. /api/sessions
html = re.sub(
    r"fetch\('/api/sessions'\)\s*\.then\([^)]+\)\s*\.then\(sessions => \{",
    """// MOCK SESSIONS
    Promise.resolve([
        {session_id: 'chat_session_001', turns: 3, max_sri: 15, max_decision: 'SAFE'},
        {session_id: 'evasion_demo_01', turns: 4, max_sri: 100, max_decision: 'BLOCKED'}
    ]).then(sessions => {""",
    html
)

# 2. /api/graph/
html = re.sub(
    r"fetch\(`/api/graph/\$\{sessionId\}`\)\s*\.then\([^)]+\)\s*\.then\(data => \{",
    """// MOCK GRAPH DATA
    Promise.resolve(
        sessionId === 'evasion_demo_01' ? {
            elements: [
                {data: {id: 'n1', label: 'file_tool.read'}, classes: 'SAFE'},
                {data: {id: 'n2', label: 'database_tool.select'}, classes: 'SAFE'},
                {data: {id: 'n3', label: 'github_tool.list_repos'}, classes: 'BLOCKED'},
                {data: {id: 'e1', source: 'n1', target: 'n2'}},
                {data: {id: 'e2', source: 'n2', target: 'n3'}, classes: 'dangerous'}
            ],
            timeline: [
                {tool_name: 'file_tool', action: 'read', decision: 'SAFE', sri: 10, idx: 0},
                {tool_name: 'database_tool', action: 'select', decision: 'SAFE', sri: 20, idx: 1},
                {tool_name: 'github_tool', action: 'list_repos', decision: 'BLOCKED', sri: 100, idx: 2}
            ],
            matched_path: "PATH_ADAPTIVE_EVASION (Adaptive Evasion Recon Chain)"
        } : {
            elements: [
                {data: {id: 'n1', label: 'slack_tool.send_message'}, classes: 'SAFE'}
            ],
            timeline: [
                {tool_name: 'slack_tool', action: 'send_message', decision: 'SAFE', sri: 15, idx: 0}
            ],
            matched_path: ""
        }
    ).then(data => {""",
    html
)

# 3. /api/audit
html = re.sub(
    r"fetch\('/api/audit'\)\s*\.then\([^)]+\)\s*\.then\(logs => \{",
    """// MOCK AUDIT LOGS
    Promise.resolve([
        {timestamp: new Date().toISOString(), session_id: 'chat_session_001', tool_name: 'slack_tool', action: 'send_message', decision: 'SAFE', sri_score: 15, user_role: 'junior_analyst', policy_result: 'ALLOWED'},
        {timestamp: new Date().toISOString(), session_id: 'evasion_demo_01', tool_name: 'github_tool', action: 'list_repos', decision: 'BLOCKED', sri_score: 100, user_role: 'junior_analyst', policy_result: 'DENIED'}
    ]).then(logs => {""",
    html
)

# 4. /api/test_exploit
html = re.sub(
    r"fetch\('/api/test_exploit', \{[^}]+\}\)\s*\.then\([^)]+\)\s*\.then\(data => \{",
    """// MOCK EXPLOIT RESULT
    setTimeout(() => {
        let data = {
            sri: 100, decision: 'BLOCKED', explanation: 'Mocked explantion for presentation.',
            security: { matched_path: 'Mocked Attack Path', feature_scores: { CD: 0.8, PV: 0.9, TR: 0.6, ST: 1.0, ML: 0.95 } },
            raw_result: 'Access Denied.', sandboxed: false
        };
        """,
    html
)
html = html.replace(".catch(err => {", "}, 500); /*.catch(err => {")

with open("standalone_demo.html", "w", encoding="utf-8") as f:
    f.write(html)
