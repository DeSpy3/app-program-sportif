from datetime import date

import pytest

from app_program_sportif.core.periodization import phases_for, volume_curve
from app_program_sportif.core.plan import Phase, SessionKind
from app_program_sportif.core.profile import (
    Availability,
    Goal,
    Level,
    Profile,
    Sport,
    SportPractice,
)
from app_program_sportif.planner.endurance import build_plan


def make_profile(sport=Sport.RUNNING, goals=None):
    return Profile(
        age=25,
        weight_kg=70,
        height_cm=175,
        practices=[
            SportPractice(sport=sport, level=Level.INTERMEDIATE, weekly_hours=3)
        ],
        goals=goals or [],
        availability=Availability(
            days_per_week=4, minutes_per_session=60, unavailable_days=[6]
        ),
    )


def test_phases_for_12_weeks():
    phases = phases_for(12)
    assert len(phases) == 12
    assert phases[-1] is Phase.TAPER
    assert {Phase.BASE, Phase.BUILD, Phase.PEAK, Phase.TAPER} <= set(phases)


def test_too_short_plan_rejected():
    with pytest.raises(ValueError):
        phases_for(3)


def test_volume_progression_is_limited():
    curve = volume_curve(100, phases_for(12), cap=400)
    for i in range(1, len(curve)):
        assert curve[i] <= 1.1 * max(curve[:i]) + 1e-9


def test_deload_and_taper_are_lighter():
    curve = volume_curve(100, phases_for(12), cap=400)
    assert curve[3] < curve[2]
    assert curve[-1] < curve[-2]


def test_volume_respects_cap():
    curve = volume_curve(100, phases_for(12), cap=110)
    assert all(v <= 110 + 1e-9 for v in curve)


def test_build_plan_structure():
    plan = build_plan(make_profile(), weeks=12)
    assert len(plan.weeks) == 12
    for week in plan.weeks:
        days = [s.day for s in week.sessions]
        assert len(days) == 4
        assert len(set(days)) == 4
        assert 6 not in days
        assert week.sessions[-1].kind is SessionKind.LONG
        assert all(s.duration_min >= 20 for s in week.sessions)
        if week.is_deload:
            assert all(s.kind is not SessionKind.QUALITY for s in week.sessions)


def test_plan_length_from_goal_date():
    goal = Goal(
        sport=Sport.TRAIL, description="Trail 30 km", target_date=date(2026, 12, 29)
    )
    profile = make_profile(sport=Sport.TRAIL, goals=[goal])
    plan = build_plan(profile, today=date(2026, 10, 20))
    assert len(plan.weeks) == 10


def test_strength_only_profile_rejected():
    with pytest.raises(ValueError):
        build_plan(make_profile(sport=Sport.STRENGTH))
