# pyright: basic

from pathlib import Path

from alembic import command
from alembic.config import Config
from app.api.errors import AppError, ErrorCode, install_exception_handlers
from app.api.main import create_app
from app.api.schemas.common import OfficeHealth
from app.settings import AppSettings
from fastapi import FastAPI
from fastapi.testclient import TestClient


def migrated_app(tmp_path: Path):
    settings = AppSettings.from_env(
        env={"DOC_AGENT_DATA_DIR": str(tmp_path)},
        cwd=tmp_path,
    )
    config = Config("alembic.ini")
    config.set_main_option("script_location", "backend/migrations")
    config.set_main_option(
        "sqlalchemy.url",
        f"sqlite+pysqlite:///{settings.database_path.as_posix()}",
    )
    command.upgrade(config, "head")
    return create_app(
        settings=settings,
        office_probe=lambda: OfficeHealth(status="unavailable", detail=None),
    )


def test_health_reports_application_status(tmp_path: Path) -> None:
    with TestClient(migrated_app(tmp_path)) as client:
        response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert response.json()["database"] == "ok"
    assert response.headers["X-Request-ID"]


def test_health_initializes_configured_database(tmp_path: Path) -> None:
    local_app = migrated_app(tmp_path)
    with TestClient(local_app) as client:
        response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["database"] == "ok"
    assert (tmp_path / "app.db").exists()


def test_openapi_endpoint_exports_core_schemas(tmp_path: Path) -> None:
    with TestClient(migrated_app(tmp_path)) as client:
        response = client.get("/api/v1/openapi.json")

    assert response.status_code == 200
    schema = response.json()
    assert schema["info"]["title"] == "文档处理办公 Agent API"
    assert "ErrorResponse" in schema["components"]["schemas"]
    assert "TaskDetail" in schema["components"]["schemas"]
    assert "ExecutionEvent" in schema["components"]["schemas"]


def test_app_error_uses_unified_response() -> None:
    test_app = FastAPI()
    install_exception_handlers(test_app)

    @test_app.get("/fail")
    async def fail() -> None:
        raise AppError(
            code=ErrorCode.PATH_FORBIDDEN,
            message="路径不允许",
            status_code=403,
            details={"path": "../secret"},
        )

    response = TestClient(test_app).get(
        "/fail",
        headers={"X-Request-ID": "9f2a3dc2-4b76-4f5f-b8ee-5b04e79573ee"},
    )

    assert response.status_code == 403
    assert response.json()["code"] == "PATH_FORBIDDEN"
    assert response.json()["request_id"] == "9f2a3dc2-4b76-4f5f-b8ee-5b04e79573ee"
    assert response.headers["X-Request-ID"] == "9f2a3dc2-4b76-4f5f-b8ee-5b04e79573ee"
