from typing import cast

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from sqlalchemy import Engine, text

from app.api.schemas.common import HealthStatus

router = APIRouter()


@router.get("/health", response_model=HealthStatus)
def health(request: Request) -> HealthStatus | JSONResponse:
    engine = cast(Engine, request.app.state.database_engine)
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1")).scalar_one()
    except Exception:
        payload = HealthStatus(status="error", database="error", application="ok")
        return JSONResponse(status_code=503, content=payload.model_dump())
    return HealthStatus(status="ok", database="ok", application="ok")
