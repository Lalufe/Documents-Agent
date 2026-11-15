# pyright: basic

from app.api.errors import AppError, ErrorCode, install_exception_handlers
from app.api.main import app
from fastapi import FastAPI
from fastapi.testclient import TestClient


def test_health_reports_application_status() -> None:
    response = TestClient(app).get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert response.json()["database"] == "ok"
    assert response.headers["X-Request-ID"]


def test_openapi_endpoint_exports_core_schemas() -> None:
    response = TestClient(app).get("/api/v1/openapi.json")

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
