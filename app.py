"""SpeakMate AI — entry point.

Run locally with:  streamlit run app.py
"""
from __future__ import annotations

import sys
from pathlib import Path

# Streamlit Cloud does not always place the script's folder on sys.path, and the
# working directory can differ from the repo root. Adding it here keeps the
# local packages (components, database, pages, services, utils) importable
# wherever the app is launched from.
APP_DIR = Path(__file__).resolve().parent
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

import streamlit as st

_REQUIRED_PACKAGES = ("components", "database", "pages", "services", "utils")
_missing = [name for name in _REQUIRED_PACKAGES if not (APP_DIR / name / "__init__.py").exists()]
if _missing:
    st.error(
        "These folders are missing next to app.py: "
        + ", ".join(_missing)
        + ". Each one needs its `__init__.py` file. If you uploaded the project "
        "through the GitHub web interface, empty files are dropped silently — push "
        "with `git add -A` from the command line, or re-upload the full folder."
    )
    st.stop()

from components.sidebar import render_sidebar
from components.ui import inject_css
from database.database import init_db
from services.auth_service import refresh_current_user
from utils.config import APP_NAME, APP_TAGLINE
from utils.helpers import LOGGER

st.set_page_config(
    page_title=f"{APP_NAME} — {APP_TAGLINE}",
    page_icon="🎙️",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={"About": f"{APP_NAME} · AI speaking practice for English learners."},
)

DEFAULT_STATE = {
    "logged_in": False,
    "user": None,
    "user_id": None,
    "username": None,
    "current_page": "dashboard",
    "auth_view": "landing",
    "practice_state": {},
    "temporary_audio": None,
    "current_feedback": None,
    "login_attempts": [],
    "toast": None,
}


def bootstrap() -> None:
    for key, value in DEFAULT_STATE.items():
        st.session_state.setdefault(key, value)
    if not st.session_state.get("_db_ready"):
        try:
            init_db()
            st.session_state["_db_ready"] = True
        except Exception as exc:  # pragma: no cover - startup guard
            LOGGER.exception("Database initialisation failed: %s", exc)
            st.error(
                "The app could not open its database. Check that the data folder is "
                "writable, then reload the page."
            )
            st.stop()


def main() -> None:
    bootstrap()
    inject_css()

    if st.session_state.get("toast"):
        st.toast(st.session_state.pop("toast"))

    if not st.session_state.logged_in or not st.session_state.user:
        from pages import auth as auth_page

        auth_page.render()
        return

    fresh = refresh_current_user(st.session_state.user_id)
    if fresh is None:
        st.session_state.clear()
        st.warning("Your session ended. Sign in again to continue.")
        st.stop()
    st.session_state.user = fresh

    if not fresh.onboarded:
        from pages import onboarding

        onboarding.render(fresh)
        return

    page = render_sidebar(fresh)

    try:
        if page == "dashboard":
            from pages import dashboard as view
        elif page == "practice":
            from pages import practice as view
        elif page == "vocabulary":
            from pages import vocabulary as view
        elif page == "progress":
            from pages import progress as view
        elif page == "history":
            from pages import history as view
        elif page == "profile":
            from pages import profile as view
        elif page == "settings":
            from pages import settings as view
        elif page == "admin":
            from pages import admin as view
        else:
            from pages import dashboard as view
        view.render(fresh)
    except Exception as exc:  # never show a traceback to the user
        LOGGER.exception("Page '%s' failed: %s", page, exc)
        st.error(
            "Something went wrong loading this page. Go back to the dashboard and "
            "try again. If it keeps happening, check the server logs."
        )
        if st.button("Back to dashboard"):
            st.session_state.current_page = "dashboard"
            st.rerun()


if __name__ == "__main__":
    main()
