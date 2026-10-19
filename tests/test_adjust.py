import pytest

from app_program_sportif.core.feedback import SessionFeedback
from app_program_sportif.core.profile import (
    Availability,
    Level,
    Profile,
    Sport,
    SportPractice,
)
from app_program_sportif.planner.adjust import adjust_plan, weekly_factor
from app_program_sportif.planner.combined import build_combined_plan


def make_plan():
    profile = Profile(
        age=25,
        weight_kg=70,
        height_cm=175,
        practices=[
            SportPractice(sport=Sport.RUNNING, level=Level.INTERMEDIATE, weekly_hours=3)
        ],
        availability=Availability(
            days_per_week=4, minutes_per_session=60, unavailable_days=[6]
        ),
    )
    return build_combined_plan(profile, weeks=12)


def feedbacks(week, completed=True, delta=0):
    return [
        SessionFeedback(
            week=week.number,
            day=s.day,
            completed=completed,
            actual_rpe=max(1, min(10, s.rpe + delta)),
        )
        for s in week.sessions
    ]


def test_factor_values():
    week = make_plan().weeks[0]
    assert weekly_factor(week, []) == 1.0
    assert weekly_factor(week, feedbacks(week)) == 1.0
    assert weekly_factor(week, feedbacks(week, completed=False)) == 0.85
    assert weekly_factor(week, feedbacks(week, delta=3)) == 0.9
    assert weekly_factor(week, feedbacks(week, delta=-3)) == 1.05


def test_missed_week_lightens_next_weeks():
    plan = make_plan()
    new = adjust_plan(plan, 1, feedbacks(plan.weeks[0], completed=False))
    assert new.weeks[0] == plan.weeks[0]
    assert new.weeks[1].total_minutes < plan.weeks[1].total_minutes


def test_normal_week_keeps_plan():
    plan = make_plan()
    assert adjust_plan(plan, 1, feedbacks(plan.weeks[0])) == plan


def test_max_minutes_cap():
    plan = make_plan()
    new = adjust_plan(plan, 1, feedbacks(plan.weeks[0], delta=-3), max_minutes=30)
    assert all(s.duration_min <= 30 for w in new.weeks[1:] for s in w.sessions)


def test_unknown_week():
    with pytest.raises(ValueError):
        adjust_plan(make_plan(), 99, [])
