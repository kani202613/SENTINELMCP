with open('dashboard/templates/index.html', 'r', encoding='utf-8') as f:
    text = f.read()

for i, line in enumerate(text.splitlines()):
    if 'id="cy"' in line or "id='cy'" in line:
        print(line)
