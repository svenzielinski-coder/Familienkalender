from datetime import datetime, timedelta
from .db import SpecialDay

def dt(y, m, d):
    return datetime(y, m, d, 0, 0, 0)

def seed_2026_niedersachsen(session):
    # nur einmal seed-en
    if session.query(SpecialDay).count() > 0:
        return

    # Schulferien Niedersachsen 2026 (Ende exklusiv -> +1 Tag)
    school_breaks = [
        ("Halbjahresferien", dt(2026, 2, 2),  dt(2026, 2, 3)  + timedelta(days=1)),
        ("Osterferien",      dt(2026, 3, 23), dt(2026, 4, 7)  + timedelta(days=1)),
        ("Tag nach Himmelfahrt", dt(2026, 5, 15), dt(2026, 5, 15) + timedelta(days=1)),
        ("Pfingstferien (Ferientag)", dt(2026, 5, 26), dt(2026, 5, 26) + timedelta(days=1)),
        ("Sommerferien",     dt(2026, 7, 2),  dt(2026, 8, 12) + timedelta(days=1)),
        ("Herbstferien",     dt(2026, 10, 12),dt(2026, 10, 24)+ timedelta(days=1)),
        ("Weihnachtsferien", dt(2026, 12, 23),dt(2027, 1, 9)  + timedelta(days=1)),
    ]

    # Gesetzliche Feiertage Niedersachsen 2026 (ganztägig)
    holidays = [
        ("Neujahr", dt(2026, 1, 1), dt(2026, 1, 1) + timedelta(days=1)),
        ("Karfreitag", dt(2026, 4, 3), dt(2026, 4, 3) + timedelta(days=1)),
        ("Ostermontag", dt(2026, 4, 6), dt(2026, 4, 6) + timedelta(days=1)),
        ("Tag der Arbeit", dt(2026, 5, 1), dt(2026, 5, 1) + timedelta(days=1)),
        ("Christi Himmelfahrt", dt(2026, 5, 14), dt(2026, 5, 14) + timedelta(days=1)),
        ("Pfingstmontag", dt(2026, 5, 25), dt(2026, 5, 25) + timedelta(days=1)),
        ("Tag der Deutschen Einheit", dt(2026, 10, 3), dt(2026, 10, 3) + timedelta(days=1)),
        ("Reformationstag", dt(2026, 10, 31), dt(2026, 10, 31) + timedelta(days=1)),
        ("1. Weihnachtstag", dt(2026, 12, 25), dt(2026, 12, 25) + timedelta(days=1)),
        ("2. Weihnachtstag", dt(2026, 12, 26), dt(2026, 12, 26) + timedelta(days=1)),
    ]

    for title, start, end in school_breaks:
        session.add(SpecialDay(kind="school_break", title=title, start=start, end=end))

    for title, start, end in holidays:
        session.add(SpecialDay(kind="holiday", title=title, start=start, end=end))

    session.commit()
