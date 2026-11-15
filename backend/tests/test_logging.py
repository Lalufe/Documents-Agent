# pyright: basic

import json
import logging
from typing import cast
from uuid import UUID

from app.api.errors import install_exception_handlers
from app.infrastructure.observability import (
    JsonFormatter,
    configure_logging,
    log_context,
    redact_for_logging,
)
from fastapi import FastAPI
from fastapi.testclient import TestClient


class ContextLogRecord(logging.LogRecord):
    request_id: object
    fields: dict[str, object]


def test_json_formatter_includes_bound_job_context() -> None:
    record = logging.LogRecord(
        name="doc_agent.job",
        level=logging.INFO,
        pathname=__file__,
        lineno=1,
        msg="job.status",
        args=(),
        exc_info=None,
    )
    record.event = "job.status"
    record.fields = {
        "job_type": "convert",
        "phase": "validating",
        "duration_ms": 42,
    }

    with log_context(
        request_id=UUID("9f2a3dc2-4b76-4f5f-b8ee-5b04e79573ee"),
        task_id="task-1",
        turn_id="turn-1",
        job_id="job-1",
    ):
        payload = cast(dict[str, object], json.loads(JsonFormatter().format(record)))

    assert payload["event"] == "job.status"
    assert payload["level"] == "INFO"
    assert payload["request_id"] == "9f2a3dc2-4b76-4f5f-b8ee-5b04e79573ee"
    assert payload["task_id"] == "task-1"
    assert payload["turn_id"] == "turn-1"
    assert payload["job_id"] == "job-1"
    assert payload["job_type"] == "convert"
    assert payload["phase"] == "validating"
    assert payload["duration_ms"] == 42
    assert cast(str, payload["timestamp"]).endswith("Z")


def test_redaction_removes_credentials_paths_and_document_text() -> None:
    payload = {
        "api_key": "sk-live-secret",
        "authorization": "Bearer top-secret",
        "cookie": "session=private",
        "content": "完整文档正文",
        "content_hash": "abc123",
        "message": r"failed at C:\Users\Alice\Documents\private.docx",
        "nested": {
            "token": "token-value",
            "path": "/home/alice/private/report.docx",
        },
    }

    redacted = cast(dict[str, object], redact_for_logging(payload))
    serialized = json.dumps(redacted, ensure_ascii=False)

    assert redacted["api_key"] == "<redacted>"
    assert redacted["authorization"] == "<redacted>"
    assert redacted["cookie"] == "<redacted>"
    assert redacted["content"] == "<redacted>"
    assert redacted["content_hash"] == "abc123"
    assert "Alice" not in serialized
    assert "/home/alice" not in serialized
    assert "top-secret" not in serialized
    assert "token-value" not in serialized


def test_request_log_reuses_request_id_and_excludes_query() -> None:
    configure_logging("INFO")
    app = FastAPI()
    install_exception_handlers(app)

    @app.get("/items")
    async def items() -> dict[str, str]:
        return {"status": "ok"}

    records: list[logging.LogRecord] = []

    class CaptureHandler(logging.Handler):
        def emit(self, record: logging.LogRecord) -> None:
            records.append(record)

    request_logger = logging.getLogger("doc_agent.request")
    handler = CaptureHandler()
    request_logger.addHandler(handler)
    previous_level = request_logger.level
    previous_disabled = request_logger.disabled
    previous_disable = logging.root.manager.disable
    request_logger.setLevel(logging.INFO)
    request_logger.disabled = False
    logging.disable(logging.NOTSET)
    assert request_logger.isEnabledFor(logging.INFO)
    request_id = "9f2a3dc2-4b76-4f5f-b8ee-5b04e79573ee"
    try:
        response = TestClient(app).get(
            "/items?token=must-not-appear",
            headers={"X-Request-ID": request_id},
        )
    finally:
        request_logger.setLevel(previous_level)
        request_logger.disabled = previous_disabled
        logging.disable(previous_disable)
        request_logger.removeHandler(handler)

    assert response.status_code == 200
    request_records = [
        record
        for record in records
        if getattr(record, "event", None) == "http.request.completed"
    ]
    assert len(request_records) == 1
    record = cast(ContextLogRecord, request_records[0])
    assert record.request_id == request_id
    fields = record.fields
    assert fields["method"] == "GET"
    assert fields["route"] == "/items"
    assert fields["status_code"] == 200
    assert "must-not-appear" not in str(fields)
