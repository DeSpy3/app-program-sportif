"""Modèle du profil sportif de l'utilisateur."""

from datetime import date
from enum import Enum

from pydantic import BaseModel, Field, model_validator


class Sport(str, Enum):
    RUNNING = "running"
    TRAIL = "trail"
    STRENGTH = "strength"


class Level(str, Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


class SportPractice(BaseModel):
    """Pratique actuelle d'un sport."""

    sport: Sport
    level: Level
    weeks_of_practice: int = Field(default=0, ge=0)
    weekly_hours: float = Field(default=0, ge=0, le=40)


class Goal(BaseModel):
    """Objectif lié à un sport."""

    sport: Sport
    description: str
    target_date: date | None = None
    distance_km: float | None = Field(default=None, gt=0)
    elevation_gain_m: float | None = Field(default=None, ge=0)


class Availability(BaseModel):
    """Disponibilités hebdomadaires. Jours : 0 = lundi ... 6 = dimanche."""

    days_per_week: int = Field(ge=1, le=7)
    minutes_per_session: int = Field(ge=15, le=240)
    unavailable_days: list[int] = Field(default_factory=list)

    @model_validator(mode="after")
    def _check_days(self):
        days = set(self.unavailable_days)
        if any(d < 0 or d > 6 for d in days):
            raise ValueError("Les jours doivent être compris entre 0 et 6")
        if 7 - len(days) < self.days_per_week:
            raise ValueError("Pas assez de jours disponibles")
        return self


class Profile(BaseModel):
    age: int = Field(ge=16, le=100)
    weight_kg: float = Field(gt=0)
    height_cm: float = Field(gt=0)
    practices: list[SportPractice] = Field(min_length=1)
    # Familles de sports choisies par l'utilisateur (ex. running + trail).
    sport_groups: list[list[Sport]] = Field(default_factory=list)
    goals: list[Goal] = Field(default_factory=list)
    availability: Availability
    equipment: list[str] = Field(default_factory=list)
    injuries: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def _check_consistency(self):
        sports = [p.sport for p in self.practices]
        if len(sports) != len(set(sports)):
            raise ValueError("Un sport ne peut apparaître qu'une fois")
        grouped = [s for g in self.sport_groups for s in g]
        if len(grouped) != len(set(grouped)):
            raise ValueError("Un sport ne peut être que dans un seul groupe")
        if not set(grouped) <= set(sports):
            raise ValueError("Un groupe contient un sport non pratiqué")
        for goal in self.goals:
            if goal.sport not in sports:
                raise ValueError("Un objectif vise un sport non pratiqué")
        return self

    def family_of(self, sport: Sport) -> frozenset[Sport]:
        """Retourne la famille de sports à laquelle appartient `sport`."""
        for group in self.sport_groups:
            if sport in group:
                return frozenset(group)
        return frozenset({sport})


def suggest_groups(sports: list[Sport]) -> list[list[Sport]]:
    """Suggestion par défaut, que l'utilisateur doit confirmer."""
    if {Sport.RUNNING, Sport.TRAIL} <= set(sports):
        return [[Sport.RUNNING, Sport.TRAIL]]
    return []
