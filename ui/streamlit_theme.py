"""Load premium CSS for Streamlit — presentation only."""

from __future__ import annotations

from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent


def inject_premium_ui(theme: str) -> None:
    import streamlit as st

    css = (_ROOT / "static" / "css" / "premium.css").read_text(encoding="utf-8")
    if (theme or "").strip().lower() == "light":
        css += "\n" + (_ROOT / "static" / "css" / "theme_light_overrides.css").read_text(
            encoding="utf-8"
        )
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)
