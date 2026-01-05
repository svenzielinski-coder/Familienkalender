import streamlit as st
import pandas as pd
from datetime import datetime, timedelta, date, time

from PIL import Image
import pytesseract
from streamlit_mic_recorder import speech_to_text
from streamlit_calendar import calendar

from src.auth import require_login
from src.db import get_session, Event, SpecialDay
from src.seed_special_days import seed_2026_niedersachsen
from src.intake import suggest_event_fields

st.set_page_config(page_title="Familienkalender 2026", layout="wide")

# --------------------
# Login
# --------------------
require_login()

# --------------------
# DB + Seed
# --------------------
session = get_session()
seed_2026_niedersachsen(session)

# --------------------
# Farben
# --------------------
owner_colors = {
    "Mama": "#3b82f6",
    "Papa": "#22c55e",
    "Kind1": "#f97316",
    "Kind2": "#a855f7",
    "Alle": "#111827",
}

st.title("📅 Familienkalender 2026 (Niedersachsen)")

# ==========================================
# Sidebar: Schnellerfassung + Formular
# ==========================================
st.sidebar.header("⚡ Schnellerfassung (Kamera / Sprache)")

# Session defaults fürs Formular
if "form_title" not in st.session_state:
    st.session_state.form_title = ""
if "form_owner" not in st.session_state:
    st.session_state.form_owner = "Alle"
if "form_start_day" not in st.session_state:
    st.session_state.form_start_day = date(2026, 1, 1)
if "form_start_time" not in st.session_state:
    st.session_state.form_start_time = time(9, 0)
if "form_end_day" not in st.session_state:
    st.session_state.form_end_day = date(2026, 1, 1)
if "form_end_time" not in st.session_state:
    st.session_state.form_end_time = time(10, 0)
if "form_notes" not in st.session_state:
    st.session_state.form_notes = ""

def apply_suggestions(raw_text: str):
    sug = suggest_event_fields(raw_text)
    if sug["title"]:
        st.session_state.form_title = sug["title"]
    st.session_state.form_start_day = sug["start_date"]
    st.session_state.form_start_time = sug["start_time"]
    st.session_state.form_end_day = sug["end_date"]
    st.session_state.form_end_time = sug["end_time"]
    st.session_state.form_notes = sug["notes"]

# --- Kamera OCR ---
with st.sidebar.expander("📷 Kamera: Termin abfotografieren (OCR)", expanded=False):
    img_file = st.camera_input("Foto aufnehmen")
    if img_file is not None:
        img = Image.open(img_file)
        st.image(img, caption="Aufgenommenes Bild", use_container_width=True)

        if st.button("Text aus Bild erkennen (OCR)"):
            try:
                text = pytesseract.image_to_string(img, lang="deu")
            except Exception as e:
                st.error("OCR fehlgeschlagen. Ist Tesseract installiert + deutsches Sprachpaket vorhanden?")
                st.exception(e)
                text = ""

            if text.strip():
                st.text_area("Erkannter Text", value=text, height=160)
                if st.button("Als Termin-Vorschlag übernehmen"):
                    apply_suggestions(text)
                    st.success("Vorbefüllt ✅ (bitte kurz prüfen)")
                    st.rerun()
            else:
                st.warning("Kein Text erkannt. Tipp: gute Beleuchtung, scharfes Bild, nah ran.")

# --- Sprache ---
with st.sidebar.expander("🎙️ Sprache: Termin diktieren", expanded=False):
    st.caption("Beispiel: „Arzttermin am 12.01. um 15:00 bis 16:00 für Mama“")
    transcript = speech_to_text(
        language="de",
        start_prompt="Aufnahme starten",
        stop_prompt="Stop",
        just_once=True,
        use_container_width=True,
        key="stt"
    )
    if transcript:
        st.text_area("Transkript", value=transcript, height=120)
        if st.button("Als Termin-Vorschlag übernehmen", key="apply_stt"):
            apply_suggestions(transcript)
            st.success("Vorbefüllt ✅ (bitte kurz prüfen)")
            st.rerun()

st.sidebar.divider()

# --- Termin hinzufügen ---
st.sidebar.header("➕ Termin hinzufügen")

title = st.sidebar.text_input("Titel", key="form_title")
owner = st.sidebar.selectbox("Person", ["Mama", "Papa", "Kind1", "Kind2", "Alle"], key="form_owner")

start_day = st.sidebar.date_input("Startdatum", key="form_start_day")
start_time = st.sidebar.time_input("Startzeit", key="form_start_time")

end_day = st.sidebar.date_input("Enddatum", key="form_end_day")
end_time = st.sidebar.time_input("Endzeit", key="form_end_time")

notes = st.sidebar.text_area("Notizen", key="form_notes")

if st.sidebar.button("Speichern"):
    if not title.strip():
        st.sidebar.error("Bitte Titel eingeben.")
    else:
        start_dt = datetime.combine(start_day, start_time)
        end_dt = datetime.combine(end_day, end_time)
        if end_dt <= start_dt:
            st.sidebar.error("Ende muss nach Start liegen.")
        else:
            ev = Event(
                title=title.strip(),
                owner=owner,
                start=start_dt,
                end=end_dt,
                notes=notes.strip() or None
            )
            session.add(ev)
            session.commit()
            st.sidebar.success("Termin gespeichert ✅")
            st.rerun()

# ===========================
# Daten laden
# ===========================
events = session.query(Event).all()
specials = session.query(SpecialDay).all()

# ===========================
# Kalender-Events bauen
# ===========================
cal_events = []

# Normale Termine
for e in events:
    c = owner_colors.get(e.owner, "#64748b")
    cal_events.append({
        "title": f"{e.title} ({e.owner})",
        "start": e.start.isoformat(),
        "end": e.end.isoformat(),
        "backgroundColor": c,
        "borderColor": c,
    })

# Ferien/Feiertage als Hintergrundflächen (klar erkennbar)
for s in specials:
    if s.kind == "holiday":
        bg = "#ef4444"   # rot
        emoji = "🎉"
    else:
        bg = "#eab308"   # gelb
        emoji = "🏫"

    cal_events.append({
        "title": f"{emoji} {s.title}",
        "start": s.start.date().isoformat(),
        "end": s.end.date().isoformat(),  # end exklusiv
        "allDay": True,
        "display": "background",
        "backgroundColor": bg,
    })

# ===========================
# Layout: links Kalender / rechts 14 Tage
# ===========================
left, right = st.columns([2.2, 1])

with left:
    st.subheader("🗓️ Kalenderansicht")
    st.caption("Ferien (gelb) & Feiertage (rot) erscheinen als Hintergrund. Termine sind farbig pro Person.")

    options = {
        "initialView": "dayGridMonth",
        "initialDate": "2026-01-01",
        "headerToolbar": {
            "left": "prev,next today",
            "center": "title",
            "right": "dayGridMonth,timeGridWeek,listMonth"
        },
        "firstDay": 1,     # Montag
        "height": 760,
        "validRange": {"start": "2026-01-01", "end": "2027-01-01"},
    }

    calendar(events=cal_events, options=options, key="cal")

with right:
    st.subheader("🔎 Nächste 14 Tage")

    now = datetime.now()
    end_window = now + timedelta(days=14)

    upcoming_events = (
        session.query(Event)
        .filter(Event.end >= now)
        .filter(Event.start <= end_window)
        .all()
    )

    upcoming_specials = (
        session.query(SpecialDay)
        .filter(SpecialDay.end >= now)
        .filter(SpecialDay.start <= end_window)
        .all()
    )

    rows = []

    for e in upcoming_events:
        rows.append({
            "sort": e.start,
            "Typ": "Termin",
            "Datum": e.start.strftime("%a, %d.%m.%Y"),
            "Zeit": f"{e.start:%H:%M}–{e.end:%H:%M}",
            "Titel": e.title,
            "Person": e.owner,
            "Hinweis": e.notes or "",
        })

    for s in upcoming_specials:
        rows.append({
            "sort": s.start,
            "Typ": "Feiertag" if s.kind == "holiday" else "Ferien",
            "Datum": s.start.strftime("%a, %d.%m.%Y"),
            "Zeit": "ganztägig",
            "Titel": s.title,
            "Person": "",
            "Hinweis": "",
        })

    if not rows:
        st.info("In den nächsten 14 Tagen keine Termine.")
    else:
        df = pd.DataFrame(rows).sort_values("sort").drop(columns=["sort"])
        st.dataframe(df, use_container_width=True, hide_index=True, height=540)

st.divider()

# ===========================
# Termine verwalten: Liste + Löschen
# ===========================
st.subheader("🧾 Termine verwalten")

if not events:
    st.info("Noch keine Termine angelegt.")
else:
    for e in sorted(events, key=lambda x: x.start):
        cols = st.columns([5, 3, 2])
        cols[0].write(f"**{e.title}**  \n{e.start:%d.%m.%Y %H:%M} – {e.end:%d.%m.%Y %H:%M}")
        cols[1].write(f"👤 {e.owner}" + (f"  \n📝 {e.notes}" if e.notes else ""))
        if cols[2].button("🗑️ Löschen", key=f"del_{e.id}"):
            session.delete(e)
            session.commit()
            st.rerun()
