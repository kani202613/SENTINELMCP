import re

def clean_ui(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        text = f.read()

    pattern = re.compile(r'<div class="card" style="padding: 12px 18px; margin-bottom: 4px;">.*?<!-- Main Grid Layout -->', re.DOTALL)
    
    clean_block = """
                <!-- Hidden inputs for JS to function without cluttering UI -->
                <input type="hidden" id="chat-session-id" value="chat_session_001">
                
                <div style="display: flex; justify-content: flex-end; margin-bottom: 10px; align-items: center; gap: 10px;">
                    <span style="font-size: 11px; font-weight: 600; color: var(--text-secondary);">USER ROLE:</span>
                    <select id="chat-user-role" style="width: auto; padding: 4px 8px; font-size: 11px; border-radius: var(--radius-sm); border: 1px solid var(--border-color); background: var(--panel-card-bg); color: var(--text-primary); cursor: pointer;">
                        <option value="junior_analyst" selected>junior_analyst</option>
                        <option value="senior_analyst">senior_analyst</option>
                        <option value="developer">developer</option>
                        <option value="lead_engineer">lead_engineer</option>
                        <option value="admin">admin</option>
                    </select>
                </div>
                
                <!-- Main Grid Layout -->
    """
    
    new_text = re.sub(pattern, clean_block.strip(), text, count=1)
    
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(new_text)

clean_ui("dashboard/templates/index.html")
clean_ui("standalone_demo.html")
