import re

with open("standalone_demo.html", "r", encoding="utf-8") as f:
    text = f.read()

# Define the messy block to replace
start_idx = text.find('<div class="card" style="padding: 12px 18px; margin-bottom: 4px;">')
end_idx = text.find('<!-- AI CHAT WINDOW -->')

if start_idx != -1 and end_idx != -1:
    old_block = text[start_idx:end_idx]
    
    clean_block = """
                <!-- Hidden inputs for JS to function without cluttering UI -->
                <input type="hidden" id="chat-session-id" value="chat_session_001">
                
                <div style="display: flex; justify-content: flex-end; margin-bottom: 10px; align-items: center; gap: 10px;">
                    <span style="font-size: 11px; font-weight: 600; color: var(--text-secondary);">Role:</span>
                    <select id="chat-user-role" style="width: auto; padding: 4px 8px; font-size: 11px; border-radius: var(--radius-sm); border: 1px solid var(--border-color); background: var(--panel-card-bg); color: var(--text-primary); cursor: pointer;">
                        <option value="junior_analyst" selected>junior_analyst</option>
                        <option value="senior_analyst">senior_analyst</option>
                        <option value="developer">developer</option>
                        <option value="lead_engineer">lead_engineer</option>
                        <option value="admin">admin</option>
                    </select>
                </div>
                
                """
    
    text = text[:start_idx] + clean_block + text[end_idx:]

with open("standalone_demo.html", "w", encoding="utf-8") as f:
    f.write(text)
