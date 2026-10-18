"""Questionnaire en ligne de commande qui construit un Profile."""

from collections.abc import Callable

from pydantic import ValidationError

from .profile import (
    Availability,
    Goal,
    Level,
    Profile,
    Sport,
    SportPractice,
    suggest_groups,
)

Ask = Callable[[str], str]

SPORT_LABELS = {
    Sport.RUNNING: "Course à pied",
    Sport.TRAIL: "Trail",
    Sport.STRENGTH: "Musculation / renforcement",
}
LEVEL_LABELS = {
    Level.BEGINNER: "Débutant",
    Level.INTERMEDIATE: "Intermédiaire",
    Level.ADVANCED: "Avancé",
}
DAY_LABELS = {
    0: "Lundi", 1: "Mardi", 2: "Mercredi", 3: "Jeudi",
    4: "Vendredi", 5: "Samedi", 6: "Dimanche",
}


def ask_number(ask: Ask, question: str, cast=int, minimum=None, maximum=None):
    while True:
        try:
            value = cast(ask(question + " ").strip().replace(",", "."))
        except ValueError:
            print("Merci d'entrer un nombre.")
            continue
        if (minimum is not None and value < minimum) or (
            maximum is not None and value > maximum
        ):
            print(f"La valeur doit être entre {minimum} et {maximum}.")
            continue
        return value


def ask_yes_no(ask: Ask, question: str) -> bool:
    return ask(question + " (o/n) ").strip().lower().startswith("o")


def ask_choices(ask: Ask, question: str, labels: dict, allow_empty=False) -> list:
    items = list(labels)
    print(question)
    for i, item in enumerate(items, 1):
        print(f"  {i}. {labels[item]}")
    while True:
        raw = ask("Numéros séparés par des virgules : ").strip()
        try:
            numbers = [int(x) for x in raw.split(",") if x.strip()]
            if any(n < 1 or n > len(items) for n in numbers):
                raise ValueError
        except ValueError:
            print("Choix invalide.")
            continue
        picked = list(dict.fromkeys(items[n - 1] for n in numbers))
        if picked or allow_empty:
            return picked
        print("Choisis au moins une option.")


def ask_one(ask: Ask, question: str, labels: dict):
    while True:
        picked = ask_choices(ask, question, labels)
        if len(picked) == 1:
            return picked[0]
        print("Un seul choix attendu.")


def ask_list(ask: Ask, question: str) -> list[str]:
    raw = ask(question + " (séparés par des virgules, vide si aucun) : ")
    return [x.strip() for x in raw.split(",") if x.strip()]


def build_profile(ask: Ask = input) -> Profile:
    age = ask_number(ask, "Âge ?", int, 16, 100)
    weight = ask_number(ask, "Poids (kg) ?", float, 20, 300)
    height = ask_number(ask, "Taille (cm) ?", float, 100, 250)

    sports = ask_choices(ask, "Quels sports pratiques-tu ou veux-tu pratiquer ?", SPORT_LABELS)

    practices = []
    for sport in sports:
        name = SPORT_LABELS[sport]
        level = ask_one(ask, f"Niveau en {name} ?", LEVEL_LABELS)
        weeks = ask_number(ask, f"Depuis combien de semaines pratiques-tu {name} ?", int, 0)
        hours = ask_number(ask, f"Heures par semaine en {name} ?", float, 0, 40)
        practices.append(
            SportPractice(sport=sport, level=level, weeks_of_practice=weeks, weekly_hours=hours)
        )

    groups = suggest_groups(sports)
    if groups and not ask_yes_no(
        ask, "Considères-tu la course à pied et le trail comme une même catégorie ?"
    ):
        groups = []

    goals = []
    for sport in sports:
        if ask_yes_no(ask, f"As-tu un objectif en {SPORT_LABELS[sport]} ?"):
            description = ask("Décris-le : ").strip()
            goals.append(Goal(sport=sport, description=description))

    while True:
        days = ask_number(ask, "Séances par semaine ?", int, 1, 7)
        minutes = ask_number(ask, "Durée d'une séance (minutes) ?", int, 15, 240)
        unavailable = ask_choices(
            ask, "Jours où tu n'es jamais disponible ?", DAY_LABELS, allow_empty=True
        )
        try:
            availability = Availability(
                days_per_week=days, minutes_per_session=minutes, unavailable_days=unavailable
            )
            break
        except ValidationError:
            print("Pas assez de jours disponibles pour ce nombre de séances, recommence.")

    equipment = ask_list(ask, "Matériel disponible ?")
    injuries = ask_list(ask, "Blessures ou zones à ménager ?")

    return Profile(
        age=age,
        weight_kg=weight,
        height_cm=height,
        practices=practices,
        sport_groups=groups,
        goals=goals,
        availability=availability,
        equipment=equipment,
        injuries=injuries,
    )
