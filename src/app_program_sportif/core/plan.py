"""Structures d'un plan d'entraînement."""

from enum import Enum

from pydantic import BaseModel, Field

from .profile import Sport


class Phase(str, Enum):
    BASE = "base"
    BUILD = "build"
    PEAK = "peak"
    TAPER = "taper"


class SessionKind(str, Enum):
    EASY = "easy"
    LONG = "long"
    QUALITY = "quality"


class Session(BaseModel):
    day: int = Field(ge=0, le=6)  # 0 = lundi ... 6 = dimanche
    sport: Sport
    kind: SessionKind
    duration_min: int = Field(gt=0)
    rpe: int = Field(ge=1, le=10)  # effort perçu
    notes: str = ""


class Week(BaseModel):
    number: int = Field(ge=1)
    phase: Phase
    is_deload: bool = False
    total_minutes: int
    sessions: list[Session]


class Plan(BaseModel):
    weeks: list[Week]
