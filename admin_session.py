"""Yönetim paneli: tam sayfa yenilemede (F5) oturum için URL token (session_state silinir)."""
import hmac
import hashlib


def _session_key() -> bytes:
    try:
        import streamlit as st

        s = st.secrets.get("ADMIN_SESSION_KEY", None)
        if s:
            return str(s).encode("utf-8")
    except Exception:
        pass
    return b"RandevuTakip-dev-ADMIN_SESSION_KEY"


def admin_session_token() -> str:
    return hmac.new(_session_key(), b"yonetim_paneli_v1", hashlib.sha256).hexdigest()


def admin_session_verify(token: str | None) -> bool:
    if not token:
        return False
    try:
        return hmac.compare_digest(admin_session_token(), str(token))
    except Exception:
        return False
