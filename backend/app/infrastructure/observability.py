from __future__ import annotations

import json
import logging
import re
import sys
from collections.abc import Generator, Iterable
from contextlib import contextmanager
from contextvars import ContextVar
from datetime import UTC, datetime
from pathlib import Path
from typing import cast

_CONTEXT_KEYS = (
    "request_id",
    "task_id",
    "turn_id",
    "job_id",
    "job_type",
    "dependency_depth",
    "source_job_ids",
    "artifact_id",
    "tool",
    "phase",
)

_SENSITIVE_KEYS = {
    "api_key",
    "apikey",
    "authorization",
    "content",
    "cookie",
    "document",
    "document_text",
    "instruction",
    "password",
    "passwd",
    "prompt",
    "refresh_token",
    "secret",
    "set-cookie",
    "text",
    "token",
}

_WINDOWS_PATH = re.compile(r"(?i)\b[A-Za-z]:[\\/][^\s\"']+")
_UNC_PATH = re.compile(r"\\\\[^\\/\s]+[\\/][^\s\"']+")
_POSIX_PRIVATE_PATH = re.compile(
    r"(?<![\w:])/(?:Users|home|tmp|var|mnt|opt)/[^\s\"']+"
)
_BEARER_TOKEN = re.compile(r"(?i)\bBearer\s+\S+")
_OPENAI_KEY = re.compile(r"\bsk-[A-Za-z0-9_-]+\b")

_LOG_CONTEXT: ContextVar[dict[str, object] | None] = ContextVar(
    "log_context",
    default=None,
)
_configured_level: str | None = None


def _redact_string(value: str) -> str:
    redacted = _BEARER_TOKEN.sub("Bearer <redacted>", value)
    redacted = _OPENAI_KEY.sub("<redacted>", redacted)
    redacted = _WINDOWS_PATH.sub("<redacted-path>", redacted)
    redacted = _UNC_PATH.sub("<redacted-path>", redacted)
    return _POSIX_PRIVATE_PATH.sub("<redacted-path>", redacted)


def redact_for_logging(value: object) -> object:
    if isinstance(value, dict):
        result: dict[str, object] = {}
        mapping = cast(dict[object, object], value)
        for raw_key, raw_value in mapping.items():
            key = str(raw_key)
            if key.lower() in _SENSITIVE_KEYS:
                result[key] = "<redacted>"
            else:
                result[key] = redact_for_logging(raw_value)
        return result
    if isinstance(value, (list, tuple, set)):
        sequence = cast(Iterable[object], value)
        return [redact_for_logging(item) for item in sequence]
    if isinstance(value, Path):
        return "<redacted-path>"
    if isinstance(value, str):
        return _redact_string(value)
    return value


def current_log_context() -> dict[str, object]:
    return dict(_LOG_CONTEXT.get() or {})


@contextmanager
def log_context(**fields: object) -> Generator[None, None, None]:
    merged = current_log_context()
    merged.update(fields)
    token = _LOG_CONTEXT.set(merged)
    try:
        yield
    finally:
        _LOG_CONTEXT.reset(token)


def log_event(
    event: str,
    *,
    level: int = logging.INFO,
    logger_name: str = "doc_agent",
    **fields: object,
) -> None:
    context = current_log_context()
    extra: dict[str, object] = {
        "event": event,
        "fields": fields,
    }
    for key in _CONTEXT_KEYS:
        if key in context:
            extra[key] = context[key]
    logging.getLogger(logger_name).log(level, event, extra=extra)


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        timestamp = datetime.now(UTC).isoformat().replace("+00:00", "Z")
        payload: dict[str, object] = {
            "timestamp": timestamp,
            "level": record.levelname,
            "event": getattr(record, "event", record.getMessage()),
            "logger": record.name,
        }
        context = current_log_context()
        for key in _CONTEXT_KEYS:
            value = getattr(record, key, context.get(key))
            if value is not None:
                payload[key] = value
        fields = getattr(record, "fields", {})
        if isinstance(fields, dict):
            redacted_fields = redact_for_logging(cast(dict[object, object], fields))
            if isinstance(redacted_fields, dict):
                payload.update(cast(dict[str, object], redacted_fields))
        redacted = redact_for_logging(payload)
        return json.dumps(redacted, ensure_ascii=False, default=str, separators=(",", ":"))


def configure_logging(level: str) -> None:
    global _configured_level
    normalized_level = level.upper()
    root = logging.getLogger()
    if normalized_level == _configured_level and any(
        getattr(handler, "_doc_agent_json", False) for handler in root.handlers
    ):
        return
    handler = logging.StreamHandler(sys.stderr)
    handler.setFormatter(JsonFormatter())
    handler._doc_agent_json = True  # type: ignore[attr-defined]
    root.handlers = [handler]
    root.setLevel(normalized_level)
    logging.getLogger("uvicorn.access").disabled = True
    _configured_level = normalized_level
