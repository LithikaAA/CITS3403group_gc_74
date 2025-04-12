import os

folders = [
    "app/routes", "app/templates", "app/static",
    "tests", "deliverables"
]
files = [
    "app/__init__.py", "app/models.py",
    "run.py", "requirements.txt", "README.md", ".gitignore"
]

for folder in folders:
    os.makedirs(folder, exist_ok=True)

for file in files:
    with open(file, "w") as f:
        f.write("")
