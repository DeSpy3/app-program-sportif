"""Construction d'un plan de musculation / renforcement musculaire."""

from datetime import date

from ..core.periodization import is_deload, phases_for
from ..core.plan import Phase, Plan, Session, SessionKind, Week
from ..core.profile import Profile, Sport
from .endurance import pick_days, plan_length

MAX_SESSIONS = 5
DELOAD_FACTOR = 0.75
# phase -> (séries x répétitions, effort perçu)
SCHEMES = {
    Phase.BASE: ("3 x 10-12", 6),
    Phase.BUILD: ("4 x 8-10", 7),
    Phase.PEAK: ("4 x 5-6", 8),
    Phase.TAPER: ("2 x 8", 5),
}
DELOAD_SCHEME = ("2 x 10", 5)
FOCUS = {
    "Corps entier A": "squat, développé couché, rowing, gainage",
    "Corps entier B": "soulevé de terre roumain, développé militaire, tractions, fentes",
    "Corps entier C": "presse à cuisses, dips, tirage horizontal, mollets",
    "Haut du corps": "développé couché, tractions, développé militaire, rowing, curl",
    "Bas du corps": "squat, soulevé de terre roumain, fentes, mollets, gainage",
}


def session_names(n: int) -> list[str]:
    if n <= 3:
        return ["Corps entier A", "Corps entier B", "Corps entier C"][:n]
    if n == 4:
        return ["Haut du corps", "Bas du corps"] * 2
    names = ["Haut du corps", "Bas du corps", "Corps entier A"]
    return (names + ["Haut du corps", "Bas du corps"])[:n]


def build_strength_weeks(
    profile: Profile, n_weeks: int, days: list[int]
) -> list[Week]:
    phases = phases_for(n_weeks)
    names = session_names(len(days))
    base = max(20, min(60, profile.availability.minutes_per_session))
    injuries = ", ".join(profile.injuries)

    weeks = []
    for number, phase in enumerate(phases, 1):
        deload = is_deload(number, phase)
        scheme, rpe = DELOAD_SCHEME if deload else SCHEMES[phase]
        duration = base
        if deload:
            duration = max(20, 5 * round(base * DELOAD_FACTOR / 5))
        sessions = []
        for day, name in zip(days, names):
            notes = f"{name} : {FOCUS[name]} ({scheme} reps)"
            if injuries:
                notes += f" - à adapter : {injuries}"
            sessions.append(
                Session(
                    day=day,
                    sport=Sport.STRENGTH,
                    kind=SessionKind.STRENGTH,
                    duration_min=duration,
                    rpe=rpe,
                    notes=notes,
                )
            )
        weeks.append(
            Week(
                number=number,
                phase=phase,
                is_deload=deload,
                total_minutes=sum(s.duration_min for s in sessions),
                sessions=sessions,
            )
        )
    return weeks


def build_strength_plan(
    profile: Profile, weeks: int | None = None, today: date | None = None
) -> Plan:
    if Sport.STRENGTH not in {p.sport for p in profile.practices}:
        raise ValueError("Aucune musculation dans le profil")
    n_weeks = weeks or plan_length(profile, Sport.STRENGTH, today)
    days = pick_days(profile.availability)[:MAX_SESSIONS]
    return Plan(weeks=build_strength_weeks(profile, n_weeks, days))
