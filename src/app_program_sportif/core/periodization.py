"""Règles de périodisation : phases et courbe de volume."""

from .plan import Phase

DELOAD_EVERY = 4
MAX_WEEKLY_INCREASE = 0.10
DELOAD_FACTOR = 0.7
TAPER_FACTOR = 0.6


def phases_for(n_weeks: int) -> list[Phase]:
    """Répartit les semaines entre les phases."""
    if n_weeks < 4:
        raise ValueError("Un plan doit durer au moins 4 semaines")
    taper = 1 if n_weeks >= 6 else 0
    peak = 1 if n_weeks >= 8 else 0
    rest = n_weeks - taper - peak
    base = rest // 2
    build = rest - base
    return (
        [Phase.BASE] * base
        + [Phase.BUILD] * build
        + [Phase.PEAK] * peak
        + [Phase.TAPER] * taper
    )


def is_deload(week_number: int, phase: Phase) -> bool:
    """Une semaine de décharge toutes les 4 semaines, en base ou développement."""
    return phase in (Phase.BASE, Phase.BUILD) and week_number % DELOAD_EVERY == 0


def volume_curve(start: float, phases: list[Phase], cap: float) -> list[float]:
    """Volume hebdomadaire (minutes) pour chaque semaine."""
    loaded = min(start, cap)
    out: list[float] = []
    for number, phase in enumerate(phases, 1):
        if phase is Phase.TAPER:
            value = loaded * TAPER_FACTOR
        elif is_deload(number, phase):
            value = loaded * DELOAD_FACTOR
        else:
            if out and phase is not Phase.PEAK:
                loaded = min(loaded * (1 + MAX_WEEKLY_INCREASE), cap)
            value = loaded
        out.append(value)
    return out
