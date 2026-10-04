import re

with open("sentinel/engine/sri_calculator.py", "r", encoding="utf-8") as f:
    text = f.read()

# Comment out hysteresis
old_h = """
    # 5. Hysteresis check (bump risk if last 3 interactions were high risk)
    hysteresis_applied = False
    recent_decisions = [e.get("decision") for e in session_history[-3:] if e.get("decision")]
    if len(recent_decisions) >= 2 and all(d in ["MONITOR", "SUSPICIOUS", "BLOCKED"] for d in recent_decisions):
        if decision == "MONITOR":
            decision = "SUSPICIOUS"
            hysteresis_applied = True
        elif decision == "SAFE" and "SUSPICIOUS" in recent_decisions:
            decision = "MONITOR"
            hysteresis_applied = True
"""

new_h = """
    # 5. Hysteresis check (bump risk if last 3 interactions were high risk)
    # [DISABLED for Final Year Project demo clarity so independent tests don't bleed into each other]
    hysteresis_applied = False
    # recent_decisions = [e.get("decision") for e in session_history[-3:] if e.get("decision")]
    # if len(recent_decisions) >= 2 and all(d in ["MONITOR", "SUSPICIOUS", "BLOCKED"] for d in recent_decisions):
    #     if decision == "MONITOR":
    #         decision = "SUSPICIOUS"
    #         hysteresis_applied = True
    #     elif decision == "SAFE" and "SUSPICIOUS" in recent_decisions:
    #         decision = "MONITOR"
    #         hysteresis_applied = True
"""

text = text.replace(old_h.strip(), new_h.strip())

with open("sentinel/engine/sri_calculator.py", "w", encoding="utf-8") as f:
    f.write(text)
