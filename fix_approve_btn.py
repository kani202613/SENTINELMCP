import re

with open("dashboard/templates/index.html", "r", encoding="utf-8") as f:
    text = f.read()

# Fix the confirmation variables
var_fix = """
    let pendingConfirmationMsg = "";
    let pendingConfirmationAttachment = null;
"""
text = re.sub(r'let pendingConfirmationMsg = "";', var_fix.strip(), text)

# Fix where it sets the confirmation
set_fix = """
                document.getElementById('chat-confirmation-box').style.display = 'flex';
                document.getElementById('confirmation-details-text').innerHTML = `Tool requested: <strong>'${res.tool}.${res.action}'</strong> (SRI Risk Score: ${res.sri}, Decision: ${res.decision}). Action modifies environment/data.`;
                pendingConfirmationMsg = message || "";
                pendingConfirmationAttachment = attachmentToSend;
"""
text = re.sub(r"document\.getElementById\('chat-confirmation-box'\)\.style\.display = 'flex';\s*document\.getElementById\('confirmation-details-text'\)\.innerHTML = [^;]+;\s*pendingConfirmationMsg = message;", set_fix.strip(), text)

# Fix the approve logic
approve_fix = """
    function submitConfirmedAction(approved) {
        if (!approved) {
            document.getElementById('chat-confirmation-box').style.display = 'none';
            let container = document.getElementById('chat-stream-container');
            let denyNotice = document.createElement('div');
            denyNotice.style.cssText = 'background: var(--sidebar-bg); border: 1px solid var(--accent-red); padding: 10px 14px; border-radius: 6px; font-size: 11px; color: var(--accent-red); font-weight: 700;';
            denyNotice.innerText = "🚫 Action DENIED by user. Tool execution was cancelled.";
            container.appendChild(denyNotice);
            container.scrollTop = container.scrollHeight;
            pendingConfirmationMsg = "";
            pendingConfirmationAttachment = null;
            return;
        }

        if (pendingConfirmationMsg !== "" || pendingConfirmationAttachment !== null) {
            let msg = pendingConfirmationMsg;
            stagedAttachment = pendingConfirmationAttachment;
            pendingConfirmationMsg = "";
            pendingConfirmationAttachment = null;
            sendChatMessage(msg, true);
        }
    }
"""

text = re.sub(r'function submitConfirmedAction\(approved\) \{[\s\S]*?\}\s*\}', approve_fix.strip(), text)

with open("dashboard/templates/index.html", "w", encoding="utf-8") as f:
    f.write(text)

# Also do it for standalone_demo.html
with open("standalone_demo.html", "r", encoding="utf-8") as f:
    text2 = f.read()

text2 = re.sub(r'let pendingConfirmationMsg = "";', var_fix.strip(), text2)
text2 = re.sub(r"document\.getElementById\('chat-confirmation-box'\)\.style\.display = 'flex';\s*document\.getElementById\('confirmation-details-text'\)\.innerHTML = [^;]+;\s*pendingConfirmationMsg = message;", set_fix.strip(), text2)
text2 = re.sub(r'function submitConfirmedAction\(approved\) \{[\s\S]*?\}\s*\}', approve_fix.strip(), text2)

with open("standalone_demo.html", "w", encoding="utf-8") as f:
    f.write(text2)
