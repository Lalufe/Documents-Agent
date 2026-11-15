from __future__ import annotations

from typing import Generic, TypeVar

from pydantic import BaseModel, ConfigDict


class ContractModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


PageItem = TypeVar("PageItem")


class CursorPage(ContractModel, Generic[PageItem]):
    items: list[PageItem]
    next_cursor: str | None
    has_more: bool


class HealthStatus(ContractModel):
    status: str
    database: str
    application: str
