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
        # 1) Bevorzugt: Klartext-Passwort aus Secrets (einfach & zuverlässig)
        plain = st.secrets.get("APP_PASSWORD", "")

        # 2) Optional weiterhin möglich: Hash
        hashed = st.secrets.get("APP_PASSWORD_HASH", "")

        if plain:
            if pw == plain:
                st.session_state.authed = True
                st.success("Angemeldet ✅")
                st.rerun()
            else:
                st.error("Falsches Passwort.")
            st.stop()

        # Wenn kein Klartext gesetzt ist, versuchen wir Hash
        if hashed:
            try:
                if pwd_context.verify(pw, hashed):
                    st.session_state.authed = True
                    st.success("Angemeldet ✅")
                    st.rerun()
                else:
                    st.error("Falsches Passwort.")
            except Exception:
                st.error("Passwort-Hash ungültig. Bitte APP_PASSWORD (Klartext) setzen.")
            st.stop()

        st.error("Kein Passwort konfiguriert. Setze APP_PASSWORD in Streamlit Secrets.")
        st.stop()

    st.stop()
