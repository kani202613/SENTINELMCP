import re

with open("dashboard/app.py", "r", encoding="utf-8") as f:
    text = f.read()

# Replace the generic read logic with PDF logic
old_logic = """
    # Read content preview
    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
    except Exception as e:
        content = f"[Binary/Unreadable file content: {e}]"
"""

new_logic = """
    # Read content preview
    content = ""
    try:
        if filename.lower().endswith('.pdf'):
            try:
                import PyPDF2
                with open(file_path, "rb") as f:
                    reader = PyPDF2.PdfReader(f)
                    for page in reader.pages:
                        text = page.extract_text()
                        if text:
                            content += text + "\\n"
            except ImportError:
                content = "[PDF parsing error: PyPDF2 not installed]"
        else:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
    except Exception as e:
        content = f"[Unreadable file content: {e}]"
"""

if old_logic.strip() in text:
    text = text.replace(old_logic.strip(), new_logic.strip())
else:
    # Use regex if exact match fails due to spaces
    text = re.sub(r'# Read content preview\s*try:\s*with open.*?except Exception as e:.*?\]"', new_logic.strip(), text, flags=re.DOTALL)

with open("dashboard/app.py", "w", encoding="utf-8") as f:
    f.write(text)
