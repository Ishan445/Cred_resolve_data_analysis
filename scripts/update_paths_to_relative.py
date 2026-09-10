import os
import re

base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

def update_file(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    orig = content
    # Replace absolute path strings
    content = content.replace(r"data/raw", "data/raw")
    content = content.replace(r"data/raw", "data/raw")
    content = content.replace(r"data/raw", "data/raw")
    content = content.replace(r"scripts", "scripts")
    content = content.replace(r"scripts", "scripts")
    content = content.replace(r"data", "data")
    content = content.replace(r"data", "data")
    content = content.replace(r"reports", "reports")
    content = content.replace(r"reports", "reports")
    content = content.replace(r".", ".")
    content = content.replace(r".", ".")

    if content != orig:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Updated: {filepath}")

# Update pipeline/
for root, _, files in os.walk(os.path.join(base_dir, "pipeline")):
    for f in files:
        if f.endswith(".py"):
            update_file(os.path.join(root, f))

# Update scripts/
for root, _, files in os.walk(os.path.join(base_dir, "scripts")):
    for f in files:
        if f.endswith(".py"):
            update_file(os.path.join(root, f))

# Update sql/
for root, _, files in os.walk(os.path.join(base_dir, "sql")):
    for f in files:
        if f.endswith(".sql"):
            update_file(os.path.join(root, f))

# Update README.md
update_file(os.path.join(base_dir, "README.md"))

print("Path normalization to data/raw complete.")
