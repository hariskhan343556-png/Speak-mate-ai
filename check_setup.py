"""Verify the project is laid out correctly before deploying.

Run from the folder containing app.py:   python check_setup.py
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PACKAGES = ["components", "database", "pages", "services", "utils"]
FILES = [
    "app.py",
    "requirements.txt",
    ".streamlit/config.toml",
    "components/sidebar.py",
    "components/ui.py",
    "components/cards.py",
    "components/charts.py",
    "components/feedback.py",
    "database/database.py",
    "database/models.py",
    "database/seed.py",
    "pages/auth.py",
    "pages/onboarding.py",
    "pages/dashboard.py",
    "pages/practice.py",
    "pages/vocabulary.py",
    "pages/progress.py",
    "pages/history.py",
    "pages/profile.py",
    "pages/settings.py",
    "pages/admin.py",
    "services/auth_service.py",
    "services/ai_service.py",
    "services/speech_service.py",
    "services/feedback_service.py",
    "services/progress_service.py",
    "utils/config.py",
    "utils/helpers.py",
    "utils/validation.py",
]

problems: list[str] = []

for package in PACKAGES:
    init = ROOT / package / "__init__.py"
    if not init.exists():
        problems.append(f"missing {package}/__init__.py")
    elif init.stat().st_size == 0:
        problems.append(f"{package}/__init__.py is empty — some upload tools drop empty files")

for relative in FILES:
    if not (ROOT / relative).exists():
        problems.append(f"missing {relative}")

if sys.version_info < (3, 11):
    problems.append(f"Python 3.11+ required, found {sys.version.split()[0]}")

if problems:
    print("Setup problems found:\n")
    for item in problems:
        print(f"  - {item}")
    print("\nFix these, then run: streamlit run app.py")
    sys.exit(1)

print(f"Layout looks correct at {ROOT}")
print("Next: pip install -r requirements.txt && streamlit run app.py")
