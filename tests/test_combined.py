import pytest

from app_program_sportif.core.plan import SessionKind
from app_program_sportif.core.profile import (
    Availability,
    Level,
    Profile,
    Sport,
    SportPractice,
)
from app_program_sportif.planner.combined import build_combined_plan


def make_profile(sports, days=4, unavailable=None):
    return Profile(
        age=25,
        weight_kg=70,
        height_cm=175,
        practices=[
            SportPractice(sport=s, level=Level.INTERMEDIATE, weekly_hours=3)
            for s in sports
        ],
        availability=Availability(
            days_per_week=days,
            minutes_per_session=60,
            unavailable_days=[6] if unavailable is None else unavailable,
        ),
    )


def long_day(week):
    return next(s.day for s in week.sessions if s.kind is SessionKind.LONG)


def test_strength_only():
    plan = build_combined_plan(make_profile([Sport.STRENGTH]), weeks=12)
    for week in plan.weeks:
        assert len(week.sessions) == 4
        assert all(s.kind is SessionKind.STRENGTH for s in week.sessions)


def test_endurance_only():
    plan = build_combined_plan(make_profile([Sport.RUNNING]), weeks=12)
    for week in plan.weeks:
        assert all(s.sport is Sport.RUNNING for s in week.sessions)


def test_combined_structure():
    plan = build_combined_plan(
        make_profile([Sport.RUNNING, Sport.STRENGTH]), weeks=12
    )
    for week in plan.weeks:
        days = [s.day for s in week.sessions]
        assert len(days) == 4
        assert len(set(days)) == 4
        assert 6 not in days
        strength = [s for s in week.sessions if s.sport is Sport.STRENGTH]
        assert len(strength) == 2
        assert all(s.day != long_day(week) - 1 for s in strength)
        assert all(s.day != long_day(week) for s in strength)


def test_combined_deload_is_lighter():
    plan = build_combined_plan(
        make_profile([Sport.TRAIL, Sport.STRENGTH]), weeks=12
    )
    assert plan.weeks[3].total_minutes < plan.weeks[2].total_minutes


def test_two_sessions_split_one_each():
    plan = build_combined_plan(
        make_profile([Sport.RUNNING, Sport.STRENGTH], days=2), weeks=8
    )
    for week in plan.weeks:
        sports = [s.sport for s in week.sessions]
        assert sports.count(Sport.STRENGTH) == 1
        assert len(sports) == 2


def test_one_session_cannot_combine():
    with pytest.raises(ValueError):
        build_combined_plan(
            make_profile([Sport.RUNNING, Sport.STRENGTH], days=1), weeks=8
        )
