"""Plan combiné : choisit la bonne construction selon les sports du profil."""

from datetime import date
from itertools import combinations, pairwise

from ..core.plan import Plan, Week
from ..core.profile import Profile, Sport
from .endurance import ENDURANCE, build_plan, pick_days, plan_length, primary_sport
from .strength import build_strength_plan, build_strength_weeks


def _min_gap(chosen: tuple[int, ...]) -> int:
    return min((b - a for a, b in pairwise(chosen)), default=7)


def split_days(days: list[int], n_strength: int) -> list[int]:
    """Choisit les jours de musculation : jamais le jour de la sortie longue
    (dernier jour), ni la veille si possible, et le plus espacés possible."""
    before_long = days[-2] if len(days) > 1 else None
    pool = [d for d in days[:-1] if d != before_long]
    if len(pool) < n_strength:
        pool = days[:-1]
    best = max(combinations(pool, n_strength), key=_min_gap)
    return list(best)


def build_combined_plan(
    profile: Profile, weeks: int | None = None, today: date | None = None
) -> Plan:
    sports = {p.sport for p in profile.practices}
    has_endurance = bool(sports & ENDURANCE)
    has_strength = Sport.STRENGTH in sports

    if has_endurance and has_strength:
        return _combine(profile, weeks, today)
    if has_endurance:
        return build_plan(profile, weeks, today)
    if has_strength:
        return build_strength_plan(profile, weeks, today)
    raise ValueError("Aucun sport pris en charge dans le profil")


def _combine(profile: Profile, weeks: int | None, today: date | None) -> Plan:
    days = pick_days(profile.availability)
    if len(days) < 2:
        raise ValueError(
            "Il faut au moins 2 séances par semaine pour combiner "
            "l'endurance et la musculation"
        )
    n_strength = max(1, min(3, len(days) // 2))
    strength_days = split_days(days, n_strength)
    endurance_days = [d for d in days if d not in strength_days]

    n_weeks = weeks or plan_length(profile, primary_sport(profile), today)
    endurance = build_plan(profile, weeks=n_weeks, today=today, days=endurance_days)
    strength = build_strength_weeks(profile, n_weeks, strength_days)

    merged = []
    for e_week, s_week in zip(endurance.weeks, strength):
        merged.append(
            Week(
                number=e_week.number,
                phase=e_week.phase,
                is_deload=e_week.is_deload,
                total_minutes=e_week.total_minutes + s_week.total_minutes,
                sessions=sorted(
                    e_week.sessions + s_week.sessions, key=lambda s: s.day
                ),
            )
        )
    return Plan(weeks=merged)
