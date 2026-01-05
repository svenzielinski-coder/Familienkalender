import streamlit as st
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_pw(pw: str, hashed: str) -> bool:
    return pwd_context.verify(pw, hashed)

def require_login():
    if "authed" not in st.session_state:
        st.session_state.authed = False

    if st.session_state.authed:
        return True

    st.title("🔐 Familienkalender – Login")
    pw = st.text_input("Passwort", type="password")

    if st.button("Anmelden"):
        hashed = st.secrets.get("APP_PASSWORD_HASH", "")
        if hashed and verify_pw(pw, hashed):
            st.session_state.authed = True
            st.success("Angemeldet ✅")
            st.rerun()
        else:
            st.error("Falsches Passwort.")

    st.stop()
