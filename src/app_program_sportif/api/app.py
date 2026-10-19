"""API web : tout est calculé à la demande, rien n'est stocké."""

from datetime import date
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, Response
from pydantic import BaseModel, Field

from ..core.feedback import SessionFeedback
from ..core.plan import Plan
from ..core.profile import Profile
from ..export.ics import next_monday, plan_to_ics
from ..planner.adjust import adjust_plan
from ..planner.combined import build_combined_plan

WEB_DIR = Path(__file__).resolve().parent.parent / "web"

app = FastAPI(title="Programme sportif")


class PlanRequest(BaseModel):
    profile: Profile
    weeks: int | None = Field(default=None, ge=4, le=24)


class AdjustRequest(BaseModel):
    plan: Plan
    week: int = Field(ge=1)
    feedbacks: list[SessionFeedback]
    max_minutes: int = Field(default=240, ge=20, le=240)


class ExportRequest(BaseModel):
    plan: Plan
    start: date | None = None


@app.get("/", include_in_schema=False)
def index() -> FileResponse:
    return FileResponse(WEB_DIR / "index.html")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/plan", response_model=Plan)
def create_plan(request: PlanRequest) -> Plan:
    try:
        return build_combined_plan(request.profile, weeks=request.weeks)
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error


@app.post("/plan/ics")
def create_ics(request: PlanRequest) -> Response:
    plan = create_plan(request)
    content = plan_to_ics(plan, next_monday(date.today()))
    return Response(content=content, media_type="text/calendar")


@app.post("/plan/adjust", response_model=Plan)
def adjust(request: AdjustRequest) -> Plan:
    try:
        return adjust_plan(
            request.plan, request.week, request.feedbacks, request.max_minutes
        )
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error


@app.post("/export/ics")
def export_ics(request: ExportRequest) -> Response:
    start = request.start or next_monday(date.today())
    content = plan_to_ics(request.plan, start)
    return Response(
        content=content,
        media_type="text/calendar",
        headers={"Content-Disposition": 'attachment; filename="plan.ics"'},
    )
