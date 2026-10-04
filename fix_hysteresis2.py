import re

with open("sentinel/engine/sri_calculator.py", "r", encoding="utf-8") as f:
    text = f.read()

pattern = re.compile(r'# 5\. Hysteresis check \(bump risk if last 3 interactions were high risk\).*?hysteresis_applied = True', re.DOTALL)

replacement = """# 5. Hysteresis check (DISABLED for Final Year Project demo clarity)
    hysteresis_applied = False
    recent_decisions = []"""

text = re.sub(pattern, replacement, text)

with open("sentinel/engine/sri_calculator.py", "w", encoding="utf-8") as f:
    f.write(text)
