# pyright: basic

from uuid import UUID

import pytest
from app.api.errors import ErrorCode, ErrorResponse
from app.api.schemas.common import CursorPage
from app.api.schemas.tasks import TaskSummary
from pydantic import ValidationError


def test_error_response_has_required_contract_fields() -> None:
    response = ErrorResponse(
        code=ErrorCode.PATH_FORBIDDEN,
        message="路径不允许",
        details={"field": "path"},
        request_id=UUID("9f2a3dc2-4b76-4f5f-b8ee-5b04e79573ee"),
    )

    assert response.model_dump(mode="json") == {
        "code": "PATH_FORBIDDEN",
        "message": "路径不允许",
        "details": {"field": "path"},
        "request_id": "9f2a3dc2-4b76-4f5f-b8ee-5b04e79573ee",
    }


def test_cursor_page_rejects_extra_fields() -> None:
    with pytest.raises(ValidationError):
        CursorPage[TaskSummary].model_validate(
            {"items": [], "next_cursor": None, "has_more": False, "total": 0}
        )


def test_task_id_is_uuid() -> None:
    summary = TaskSummary.model_validate(
        {
            "task_id": "9f2a3dc2-4b76-4f5f-b8ee-5b04e79573ee",
            "title": "读取报告",
            "status": "queued",
            "created_at": "2026-11-15T00:00:00Z",
            "updated_at": "2026-11-15T00:00:00Z",
        }
    )

    assert isinstance(summary.task_id, UUID)
