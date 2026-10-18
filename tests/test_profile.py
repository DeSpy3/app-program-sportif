import pytest
from pydantic import ValidationError

from app_program_sportif.core.profile import (
    Availability,
    Level,
    Profile,
    Sport,
    SportPractice,
    suggest_groups,
)


def make_profile(**overrides):
    data = {
        "age": 25,
        "weight_kg": 70,
        "height_cm": 175,
        "practices": [SportPractice(sport=Sport.RUNNING, level=Level.BEGINNER)],
        "availability": Availability(days_per_week=3, minutes_per_session=60),
    }
    data.update(overrides)
    return Profile(**data)


def test_valid_profile():
    assert make_profile().age == 25


def test_duplicate_sport_rejected():
    practices = [
        SportPractice(sport=Sport.RUNNING, level=Level.BEGINNER),
        SportPractice(sport=Sport.RUNNING, level=Level.ADVANCED),
    ]
    with pytest.raises(ValidationError):
        make_profile(practices=practices)


def test_group_with_unpracticed_sport_rejected():
    with pytest.raises(ValidationError):
        make_profile(sport_groups=[[Sport.RUNNING, Sport.TRAIL]])


def test_family_of_grouped_sports():
    practices = [
        SportPractice(sport=Sport.RUNNING, level=Level.INTERMEDIATE),
        SportPractice(sport=Sport.TRAIL, level=Level.BEGINNER),
    ]
    profile = make_profile(
        practices=practices, sport_groups=[[Sport.RUNNING, Sport.TRAIL]]
    )
    assert profile.family_of(Sport.TRAIL) == {Sport.RUNNING, Sport.TRAIL}


def test_suggest_groups():
    assert suggest_groups([Sport.RUNNING, Sport.TRAIL]) == [
        [Sport.RUNNING, Sport.TRAIL]
    ]
    assert suggest_groups([Sport.STRENGTH]) == []


def test_impossible_availability():
    with pytest.raises(ValidationError):
        Availability(days_per_week=5, minutes_per_session=60,
                     unavailable_days=[0, 1, 2, 3])
