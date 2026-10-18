from .core.questionnaire import build_profile


def main() -> None:
    profile = build_profile()
    print(profile.model_dump_json(indent=2))


if __name__ == "__main__":
    main()
