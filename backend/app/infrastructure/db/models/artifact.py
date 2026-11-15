from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy import (
    JSON,
    Boolean,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.db.base import (
    Base,
    empty_json_object,
    new_uuid,
    utc_now,
)


class ResultGroup(Base):
    __tablename__ = "result_groups"
    __table_args__ = (
        UniqueConstraint("job_id", name="uq_result_groups_job_id"),
        Index("ix_result_groups_task_state", "task_id", "state"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    task_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("tasks.id", ondelete="CASCADE"),
    )
    turn_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("task_turns.id", ondelete="CASCADE"),
    )
    job_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("jobs.id", ondelete="CASCADE"),
    )
    target_format: Mapped[str] = mapped_column(String(16))
    label: Mapped[str] = mapped_column(Text)
    manifest_json: Mapped[dict[str, Any]] = mapped_column(
        JSON,
        default=empty_json_object,
    )
    state: Mapped[str] = mapped_column(String(32), default="staged")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    published_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )


class Artifact(Base):
    __tablename__ = "artifacts"
    __table_args__ = (
        Index("ix_artifacts_task_kind_state", "task_id", "kind", "state"),
        Index("ix_artifacts_job_created_at", "job_id", "created_at"),
        Index("ix_artifacts_result_group_id", "result_group_id"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    task_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("tasks.id", ondelete="CASCADE"),
    )
    turn_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("task_turns.id", ondelete="CASCADE"),
    )
    job_id: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey("jobs.id", ondelete="CASCADE"),
        nullable=True,
    )
    kind: Mapped[str] = mapped_column(String(32))
    format: Mapped[str] = mapped_column(String(16))
    relative_path: Mapped[str] = mapped_column(Text)
    sha256: Mapped[str] = mapped_column(String(64))
    size_bytes: Mapped[int] = mapped_column(Integer)
    state: Mapped[str] = mapped_column(String(32), default="staged")
    is_latest_working: Mapped[bool] = mapped_column(Boolean, default=False)
    result_group_id: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey("result_groups.id", ondelete="SET NULL"),
        nullable=True,
    )
    metadata_json: Mapped[dict[str, Any]] = mapped_column(
        JSON,
        default=empty_json_object,
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    published_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
