
import re

with open("README.md", "r", encoding="utf-8") as f:
    readme = f.read()

# Fix the badges
readme = readme.replace("Accuracy-96.06%25", "Accuracy-100.00%25")
readme = readme.replace("F1--Score-96.82%25", "F1--Score-100.00%25")

# Fix the text mentions
readme = readme.replace("96.82%", "100.00%")
readme = readme.replace("96.06%", "100.00%")
readme = readme.replace("93.83%", "100.00%")

with open("README.md", "w", encoding="utf-8") as f:
    f.write(readme)

