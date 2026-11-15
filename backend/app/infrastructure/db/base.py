from __future__ import annotations

from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from sqlalchemy.orm import DeclarativeBase


def new_uuid() -> str:
    return str(uuid4())


def utc_now() -> datetime:
    return datetime.now(UTC)


def empty_json_object() -> dict[str, Any]:
    return {}


def empty_json_array() -> list[Any]:
    return []


class Base(DeclarativeBase):
    pass
