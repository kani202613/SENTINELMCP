import re

with open("standalone_demo.html", "r", encoding="utf-8") as f:
    text = f.read()

chat_mock = """
        // MOCK CHAT API
        setTimeout(() => {
            let msg = message.toLowerCase();
            let mockRes = {};
            
            if (msg.includes("hi") || msg.includes("hello") || msg.includes("hey")) {
                mockRes = {
                    thought: "The user is greeting me.",
                    action_summary: "No tool required",
                    sri: 0,
                    decision: "SAFE",
                    sandboxed: false,
                    security: {},
                    observation: "Hello! I am the SentinelMCP AI Assistant. I am ready to help you securely analyze logs, scan databases, or fetch data. How can I assist you today?"
                };
            } else if (msg.includes("who are you")) {
                mockRes = {
                    thought: "The user is asking about my identity.",
                    action_summary: "No tool required",
                    sri: 0,
                    decision: "SAFE",
                    sandboxed: false,
                    security: {},
                    observation: "I am an autonomous security agent powered by the SentinelMCP framework. I can securely execute tools while the Sentinel Interceptor evaluates my actions in real time."
                };
            } else {
                mockRes = {
                    thought: "The user requested an operation.",
                    action_summary: "simulated_tool.execute",
                    sri: 15,
                    decision: "SAFE",
                    sandboxed: false,
                    security: {},
                    observation: "### Operations Terminal\\n\\nCommand recognized for presentation mode. The proxy successfully intercepted and verified this request."
                };
            }
            
            let sendBtn = document.getElementById('chat-send-btn');
            sendBtn.disabled = false;
            let loader = document.getElementById(loadingId);
            if (loader) loader.remove();
            
            appendBotResponse(mockRes);
            updateDashboard();
        }, 1000);
        /* 
"""

text = re.sub(r"fetch\('/api/chat', \{[\s\S]*?\.catch\(err => \{[\s\S]*?console\.error\(err\);\n        \}\);", chat_mock + "*/", text)

with open("standalone_demo.html", "w", encoding="utf-8") as f:
    f.write(text)
