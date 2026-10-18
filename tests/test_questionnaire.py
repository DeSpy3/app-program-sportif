from app_program_sportif.core.profile import Sport
from app_program_sportif.core.questionnaire import build_profile


def test_build_profile_running_and_trail():
    answers = iter([
        "25", "70", "175",      # âge, poids, taille
        "1,2",                  # running + trail
        "1", "10", "3",         # running : niveau, semaines, heures
        "1", "0", "0",          # trail : niveau, semaines, heures
        "o",                    # même catégorie
        "n", "n",               # pas d'objectif
        "3", "60", "",          # séances, durée, jours indisponibles
        "chaussures",           # matériel
        "",                     # blessures
    ])
    profile = build_profile(lambda _: next(answers))
    assert len(profile.practices) == 2
    assert profile.family_of(Sport.TRAIL) == {Sport.RUNNING, Sport.TRAIL}
    assert profile.availability.days_per_week == 3
