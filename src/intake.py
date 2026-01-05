import re
from datetime import datetime, date, time, timedelta

GERMAN_MONTHS = {
    "januar": 1, "jan": 1,
    "februar": 2, "feb": 2,
    "märz": 3, "maerz": 3, "mrz": 3,
    "april": 4, "apr": 4,
    "mai": 5,
    "juni": 6, "jun": 6,
    "juli": 7, "jul": 7,
    "august": 8, "aug": 8,
    "september": 9, "sep": 9,
    "oktober": 10, "okt": 10,
    "november": 11, "nov": 11,
    "dezember": 12, "dez": 12,
}

def _clamp_2026(d: date) -> date:
    # Ziel: Jahr 2026. Wenn Text kein Jahr enthält oder anderes Jahr erwähnt:
    # -> auf 2026 setzen (für deine App).
    if d.year != 2026:
        return date(2026, d.month, d.day)
    return d

def parse_date_from_text(text: str) -> date | None:
    t = (text or "").lower()

    # dd.mm.yyyy oder dd.mm. (-> 2026)
    m = re.search(r"\b([0-3]?\d)\.([01]?\d)(?:\.(\d{4}))?\b", t)
    if m:
        d = int(m.group(1))
        mo = int(m.group(2))
        y = int(m.group(3)) if m.group(3) else 2026
        try:
            return _clamp_2026(date(y, mo, d))
        except ValueError:
            return None

    # "12. januar" / "12 januar"
    m2 = re.search(
        r"\b([0-3]?\d)\.?\s+(januar|jan|februar|feb|märz|maerz|mrz|april|apr|mai|juni|jun|juli|jul|august|aug|september|sep|oktober|okt|november|nov|dezember|dez)\b",
        t
    )
    if m2:
        d = int(m2.group(1))
        mo = GERMAN_MONTHS[m2.group(2)]
        try:
            return date(2026, mo, d)
        except ValueError:
            return None

    today = datetime.now().date()
    if "übermorgen" in t:
        return _clamp_2026(today + timedelta(days=2))
    if "morgen" in t:
        return _clamp_2026(today + timedelta(days=1))
    if "heute" in t:
        return _clamp_2026(today)

    return None

def parse_times_from_text(text: str) -> tuple[time | None, time | None]:
    t = (text or "").lower()

    # "15:30" oder "15.30"
    times = re.findall(r"\b([01]?\d|2[0-3])[:\.]([0-5]\d)\b", t)
    if times:
        sh, sm = map(int, times[0])
        start = time(sh, sm)
        end = None
        if len(times) >= 2:
            eh, em = map(int, times[1])
            end = time(eh, em)
        return start, end

    # "um 15 uhr"
    m = re.search(r"\bum\s*([01]?\d|2[0-3])\s*uhr\b", t)
    if m:
        sh = int(m.group(1))
        return time(sh, 0), None

    return None, None

def suggest_event_fields(raw_text: str) -> dict:
    """
    Liefert Vorschläge zum Vorbefüllen:
    title, start_date, start_time, end_date, end_time, notes
    """
    raw_text = (raw_text or "").strip()
    d = parse_date_from_text(raw_text)
    st_t, en_t = parse_times_from_text(raw_text)

    if d is None:
        d = date(2026, 1, 1)
    if st_t is None:
        st_t = time(9, 0)
    if en_t is None:
        en_dt = datetime.combine(d, st_t) + timedelta(minutes=60)
        en_t = en_dt.time()

    return {
        "title": raw_text[:120] if raw_text else "",
        "start_date": d,
        "start_time": st_t,
        "end_date": d,
        "end_time": en_t,
        "notes": raw_text if raw_text else "",
    }
