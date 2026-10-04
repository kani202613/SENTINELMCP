import re

with open('dashboard/templates/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Fix top buttons
html = html.replace('background: rgba(239, 68, 68, 0.12); border: 1px solid rgba(239, 68, 68, 0.3); color: var(--accent-red);', 'background: var(--panel-card-bg); border: 1px solid var(--border-color); color: var(--text-secondary);')

# Fix scenarios
html = html.replace('>Quick Scenarios:<', '>Saved Queries:<')
html = html.replace('> Benign Issue #1<', '>Scan Auth Logs<')
html = html.replace('> PDF Summary<', '>Parse Threat Report<')
html = html.replace('> DB Select<', '>Query Active Sessions<')
html = html.replace('> Indirect Injection (Issue #2)<', '>Analyze Suspicious Commit<')
html = html.replace('> DB Delete (Confirmation Test)<', '>Revoke Token (Test)<')
html = html.replace('> Slack Post<', '>Notify IR Team<')

# Remove red/green/amber styling from quick scenario buttons
html = re.sub(r'background: rgba\([^)]+\);\s*border: 1px solid [^;]+;\s*color: var\(--accent-[^)]+\);', 'background: var(--panel-card-bg); border: 1px solid var(--border-color); color: var(--text-primary);', html)

# Fix input controls
html = html.replace('placeholder=\"Enter command or search query (e.g. Analyze attached report, query employees database, read issue #1)...\"', 'placeholder=\"Enter command or query (e.g. SELECT * FROM sessions, Parse incident_report.pdf)...\"')
html = html.replace('<span>Send Prompt</span>', '<span>Execute</span>')
html = html.replace('<span> Attach File</span>', '<span style=\"color: var(--text-secondary);\">Attach File</span>')

with open('dashboard/templates/index.html', 'w', encoding='utf-8') as f:
    f.write(html)
