"""Ajustement d'un plan selon les retours de l'utilisateur."""

from collections.abc import Sequence
from statistics import mean

from ..core.feedback import SessionFeedback
from ..core.plan import Plan, Week

LOW_COMPLETION = 0.6
FATIGUE_GAP = 2


def weekly_factor(week: Week, feedbacks: Sequence[SessionFeedback]) -> float:
    """Coefficient à appliquer aux semaines suivantes.

    Une séance sans retour compte comme non réalisée.
    """
    by_day = {f.day: f for f in feedbacks if f.week == week.number}
    if not by_day:
        return 1.0
    done = 0
    gaps = []
    for session in week.sessions:
        feedback = by_day.get(session.day)
        if feedback and feedback.completed:
            done += 1
            if feedback.actual_rpe is not None:
                gaps.append(feedback.actual_rpe - session.rpe)
    completion = done / len(week.sessions)
    average_gap = mean(gaps) if gaps else 0
    if completion < LOW_COMPLETION:
        return 0.85
    if average_gap >= FATIGUE_GAP:
        return 0.9
    if completion >= 0.9 and average_gap <= -FATIGUE_GAP:
        return 1.05
    return 1.0


def adjust_plan(
    plan: Plan,
    week_number: int,
    feedbacks: Sequence[SessionFeedback],
    max_minutes: int = 240,
) -> Plan:
    """Recalcule les durées des semaines qui suivent `week_number`."""
    current = next((w for w in plan.weeks if w.number == week_number), None)
    if current is None:
        raise ValueError(f"Semaine {week_number} introuvable")
    factor = weekly_factor(current, feedbacks)
    if factor == 1.0:
        return plan

    weeks = []
    for week in plan.weeks:
        if week.number <= week_number:
            weeks.append(week)
            continue
        sessions = [
            s.model_copy(
                update={
                    "duration_min": min(
                        max_minutes, max(20, 5 * round(s.duration_min * factor / 5))
                    )
                }
            )
            for s in week.sessions
        ]
        weeks.append(
            week.model_copy(
                update={
                    "sessions": sessions,
                    "total_minutes": sum(s.duration_min for s in sessions),
                }
            )
        )
    return Plan(weeks=weeks)
