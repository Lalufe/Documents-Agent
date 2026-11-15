from __future__ import annotations

from typing import Generic, Literal, TypeVar

from pydantic import BaseModel, ConfigDict


class ContractModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


PageItem = TypeVar("PageItem")


class CursorPage(ContractModel, Generic[PageItem]):
    items: list[PageItem]
    next_cursor: str | None
    has_more: bool


class OfficeHealth(ContractModel):
    status: Literal[
        "available",
        "unavailable",
        "unsupported_platform",
        "unknown",
    ]
    detail: str | None


class HealthStatus(ContractModel):
    status: str
    application: str
    database: str
    config: str
    migrations: str
    office: OfficeHealth
