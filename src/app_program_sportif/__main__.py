from .core.questionnaire import DAY_LABELS, build_profile
from .planner.combined import build_combined_plan


def main() -> None:
    profile = build_profile()
    try:
        plan = build_combined_plan(profile)
    except ValueError as error:
        print(f"Impossible de construire le plan : {error}")
        return
    if profile.injuries:
        print("\nAttention : adapte les exercices à tes blessures et "
              "demande l'avis d'un professionnel de santé si besoin.")
    for week in plan.weeks:
        flag = " (décharge)" if week.is_deload else ""
        print(
            f"\nSemaine {week.number} - {week.phase.value}{flag}"
            f" - {week.total_minutes} min"
        )
        for s in week.sessions:
            print(
                f"  {DAY_LABELS[s.day]:<9} {s.kind.value:<8}"
                f" {s.duration_min} min  RPE {s.rpe}  {s.notes}"
            )


if __name__ == "__main__":
    main()
