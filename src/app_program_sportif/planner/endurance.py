"""Construction d'un plan d'endurance (course à pied, trail)."""

import math
from datetime import date

from ..core.periodization import is_deload, phases_for, volume_curve
from ..core.plan import Phase, Plan, Session, SessionKind, Week
from ..core.profile import Availability, Level, Profile, Sport

ENDURANCE = {Sport.RUNNING, Sport.TRAIL}
DEFAULT_START_MINUTES = {
    Level.BEGINNER: 90,
    Level.INTERMEDIATE: 180,
    Level.ADVANCED: 300,
}
WEIGHTS = {SessionKind.LONG: 2.0, SessionKind.QUALITY: 1.2, SessionKind.EASY: 1.0}
RPE = {SessionKind.LONG: 4, SessionKind.QUALITY: 7, SessionKind.EASY: 3}


def primary_sport(profile: Profile) -> Sport:
    for goal in profile.goals:
        if goal.sport in ENDURANCE:
            return goal.sport
    for practice in profile.practices:
        if practice.sport in ENDURANCE:
            return practice.sport
    raise ValueError("Aucun sport d'endurance dans le profil")


def plan_length(
    profile: Profile, sport: Sport, today: date | None = None, default: int = 12
) -> int:
    today = today or date.today()
    for goal in profile.goals:
        if goal.sport == sport and goal.target_date:
            days = (goal.target_date - today).days
            return max(4, min(24, math.ceil(days / 7)))
    return default


def pick_days(availability: Availability) -> list[int]:
    """Choisit des jours bien espacés parmi les jours disponibles."""
    free = [d for d in range(7) if d not in availability.unavailable_days]
    n = availability.days_per_week
    return [free[i * len(free) // n] for i in range(n)]


def session_kinds(n: int, phase: Phase, deload: bool) -> list[SessionKind]:
    kinds = [SessionKind.EASY] * n
    kinds[-1] = SessionKind.LONG
    if n >= 3 and phase in (Phase.BUILD, Phase.PEAK) and not deload:
        kinds[(n - 1) // 2] = SessionKind.QUALITY
    return kinds


def build_plan(
    profile: Profile, weeks: int | None = None, today: date | None = None
) -> Plan:
    sport = primary_sport(profile)
    n_weeks = weeks or plan_length(profile, sport, today)
    phases = phases_for(n_weeks)

    practice = next(p for p in profile.practices if p.sport == sport)
    start = practice.weekly_hours * 60 or DEFAULT_START_MINUTES[practice.level]
    availability = profile.availability
    cap = availability.days_per_week * availability.minutes_per_session
    volumes = volume_curve(start, phases, cap)
    days = pick_days(availability)

    result = []
    for number, (phase, volume) in enumerate(zip(phases, volumes), 1):
        deload = is_deload(number, phase)
        kinds = session_kinds(len(days), phase, deload)
        total_weight = sum(WEIGHTS[k] for k in kinds)
        sessions = []
        for day, kind in zip(days, kinds):
            raw = volume * WEIGHTS[kind] / total_weight
            duration = max(20, 5 * round(raw / 5))
            notes = ""
            if kind is SessionKind.QUALITY:
                notes = "Tempo ou fractionné"
            elif kind is SessionKind.LONG and sport is Sport.TRAIL:
                notes = "Inclure du dénivelé"
            sessions.append(
                Session(
                    day=day,
                    sport=sport,
                    kind=kind,
                    duration_min=duration,
                    rpe=RPE[kind],
                    notes=notes,
                )
            )
        result.append(
            Week(
                number=number,
                phase=phase,
                is_deload=deload,
                total_minutes=sum(s.duration_min for s in sessions),
                sessions=sessions,
            )
        )
    return Plan(weeks=result)
