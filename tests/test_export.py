from datetime import date, datetime

from app_program_sportif.core.profile import (
    Availability,
    Level,
    Profile,
    Sport,
    SportPractice,
)
from app_program_sportif.export.ics import next_monday, plan_to_ics
from app_program_sportif.planner.combined import build_combined_plan

STAMP = datetime(2026, 10, 19, 12, 0)


def make_plan():
    profile = Profile(
        age=25,
        weight_kg=70,
        height_cm=175,
        practices=[
            SportPractice(sport=Sport.RUNNING, level=Level.INTERMEDIATE, weekly_hours=3)
        ],
        availability=Availability(
            days_per_week=3, minutes_per_session=60, unavailable_days=[]
        ),
    )
    return build_combined_plan(profile, weeks=12)


def test_next_monday():
    assert next_monday(date(2026, 10, 19)) == date(2026, 10, 26)
    assert next_monday(date(2026, 10, 21)) == date(2026, 10, 26)


def test_ics_structure():
    plan = make_plan()
    text = plan_to_ics(plan, date(2026, 10, 26), stamp=STAMP)
    total = sum(len(w.sessions) for w in plan.weeks)
    assert text.startswith("BEGIN:VCALENDAR")
    assert text.count("BEGIN:VEVENT") == total
    assert "DTSTART:20261026T180000" in text
    assert "\r\n" in text


def test_ics_start_is_aligned_on_monday():
    plan = make_plan()
    monday = plan_to_ics(plan, date(2026, 10, 26), stamp=STAMP)
    wednesday = plan_to_ics(plan, date(2026, 10, 28), stamp=STAMP)
    assert monday == wednesday
