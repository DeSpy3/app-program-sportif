"""Export d'un plan au format calendrier iCalendar (.ics)."""

from datetime import date, datetime, time, timedelta, timezone

from ..core.plan import Plan, Session, SessionKind
from ..core.profile import Sport

SPORT_LABELS = {
    Sport.RUNNING: "Course",
    Sport.TRAIL: "Trail",
    Sport.STRENGTH: "Musculation",
}
KIND_LABELS = {
    SessionKind.EASY: "facile",
    SessionKind.LONG: "sortie longue",
    SessionKind.QUALITY: "qualité",
    SessionKind.STRENGTH: "",
}


def next_monday(today: date) -> date:
    """Prochain lundi strictement après `today`."""
    return today + timedelta(days=7 - today.weekday())


def _escape(text: str) -> str:
    return (
        text.replace("\\", "\\\\")
        .replace(";", "\\;")
        .replace(",", "\\,")
        .replace("\n", "\\n")
    )


def _fold(line: str) -> str:
    chunks = [line[i : i + 73] for i in range(0, len(line), 73)]
    return "\r\n ".join(chunks)


def _summary(session: Session) -> str:
    label = SPORT_LABELS[session.sport]
    kind = KIND_LABELS[session.kind]
    title = f"{label} - {kind}" if kind else label
    return f"{title} ({session.duration_min} min)"


def plan_to_ics(
    plan: Plan, start: date, hour: int = 18, stamp: datetime | None = None
) -> str:
    """Génère le calendrier. La semaine 1 commence le lundi de `start`."""
    monday = start - timedelta(days=start.weekday())
    stamp = stamp or datetime.now(timezone.utc)
    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//app-program-sportif//FR",
        "CALSCALE:GREGORIAN",
    ]
    for week in plan.weeks:
        for s in week.sessions:
            day = monday + timedelta(weeks=week.number - 1, days=s.day)
            begin = datetime.combine(day, time(hour))
            end = begin + timedelta(minutes=s.duration_min)
            description = f"Semaine {week.number} ({week.phase.value}) - RPE {s.rpe}"
            if s.notes:
                description += f" - {s.notes}"
            lines.extend(
                [
                    "BEGIN:VEVENT",
                    f"UID:{begin:%Y%m%dT%H%M}-{s.sport.value}-{s.day}@app-program-sportif",
                    f"DTSTAMP:{stamp:%Y%m%dT%H%M%SZ}",
                    f"DTSTART:{begin:%Y%m%dT%H%M%S}",
                    f"DTEND:{end:%Y%m%dT%H%M%S}",
                    f"SUMMARY:{_escape(_summary(s))}",
                    f"DESCRIPTION:{_escape(description)}",
                    "END:VEVENT",
                ]
            )
    lines.append("END:VCALENDAR")
    return "\r\n".join(_fold(line) for line in lines) + "\r\n"
