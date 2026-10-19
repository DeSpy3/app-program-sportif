from fastapi.testclient import TestClient

from app_program_sportif.api.app import app

client = TestClient(app)

PROFILE = {
    "age": 25,
    "weight_kg": 70,
    "height_cm": 175,
    "practices": [
        {
            "sport": "running",
            "level": "beginner",
            "weeks_of_practice": 10,
            "weekly_hours": 2,
        }
    ],
    "availability": {
        "days_per_week": 3,
        "minutes_per_session": 60,
        "unavailable_days": [6],
    },
}


def test_health():
    assert client.get("/health").json() == {"status": "ok"}


def test_create_plan():
    response = client.post("/plan", json={"profile": PROFILE})
    assert response.status_code == 200
    assert len(response.json()["weeks"]) == 12


def test_invalid_profile():
    bad = {**PROFILE, "age": 5}
    assert client.post("/plan", json={"profile": bad}).status_code == 422


def test_ics_endpoint():
    response = client.post("/plan/ics", json={"profile": PROFILE})
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/calendar")
    assert "BEGIN:VCALENDAR" in response.text


def test_adjust_endpoint():
    plan = client.post("/plan", json={"profile": PROFILE}).json()
    feedbacks = [
        {"week": 1, "day": s["day"], "completed": False}
        for s in plan["weeks"][0]["sessions"]
    ]
    response = client.post(
        "/plan/adjust", json={"plan": plan, "week": 1, "feedbacks": feedbacks}
    )
    assert response.status_code == 200
    new_total = response.json()["weeks"][1]["total_minutes"]
    assert new_total < plan["weeks"][1]["total_minutes"]


def test_index_page():
    response = client.get("/")
    assert response.status_code == 200
    assert "Programme sportif" in response.text


def test_export_ics_from_plan():
    plan = client.post("/plan", json={"profile": PROFILE}).json()
    response = client.post("/export/ics", json={"plan": plan, "start": "2026-10-26"})
    assert response.status_code == 200
    assert "BEGIN:VCALENDAR" in response.text
    assert "DTSTART:20261026T180000" in response.text
    assert "attachment" in response.headers["content-disposition"]
