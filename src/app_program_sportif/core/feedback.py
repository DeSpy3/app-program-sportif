"""Retour de l'utilisateur sur une séance réalisée (ou non)."""

from pydantic import BaseModel, Field


class SessionFeedback(BaseModel):
    week: int = Field(ge=1)
    day: int = Field(ge=0, le=6)  # 0 = lundi ... 6 = dimanche
    completed: bool
    actual_rpe: int | None = Field(default=None, ge=1, le=10)
