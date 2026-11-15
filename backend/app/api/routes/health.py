from fastapi import APIRouter

from app.api.schemas.common import HealthStatus

router = APIRouter()


@router.get("/health", response_model=HealthStatus)
def health() -> HealthStatus:
    return HealthStatus(status="ok", database="ok", application="ok")
