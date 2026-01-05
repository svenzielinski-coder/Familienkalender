import streamlit as st
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def require_login():
    if "authed" not in st.session_state:
        st.session_state.authed = False

    if st.session_state.authed:
        return True

    st.title("🔐 Familienkalender – Login")
    pw = st.text_input("Passwort", type="password")

    if st.button("Anmelden"):
        try:
            hashed = st.secrets.get("APP_PASSWORD_HASH", "")
            if not hashed:
                st.error("Kein Passwort konfiguriert.")
                st.stop()

            if pwd_context.verify(pw, hashed):
                st.session_state.authed = True
                st.success("Angemeldet ✅")
                st.rerun()
            else:
                st.error("Falsches Passwort.")

        except Exception as e:
            # WICHTIG: Kein Crash mehr
            st.error("Login fehlgeschlagen. Bitte Passwort erneut setzen.")
            st.stop()

    st.stop()
