from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy import (
    JSON,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.db.base import (
    Base,
    empty_json_array,
    empty_json_object,
    new_uuid,
    utc_now,
)


class Job(Base):
    __tablename__ = "jobs"
    __table_args__ = (
        Index(
            "uq_jobs_turn_artifact_slot",
            "turn_id",
            "artifact_slot",
            unique=True,
            sqlite_where=text("artifact_slot IS NOT NULL"),
        ),
        Index("ix_jobs_task_plan_index", "task_id", "plan_index"),
        Index("ix_jobs_status_dependency_state", "status", "dependency_state"),
        Index("ix_jobs_result_group_id", "result_group_id"),
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
    plan_index: Mapped[int] = mapped_column(Integer)
    job_type: Mapped[str] = mapped_column(String(32))
    goal: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(32), default="planned")
    dependency_state: Mapped[str] = mapped_column(String(32), default="waiting")
    artifact_slot: Mapped[str | None] = mapped_column(String(200), nullable=True)
    target_format: Mapped[str | None] = mapped_column(String(16), nullable=True)
    execution_spec_json: Mapped[dict[str, Any]] = mapped_column(
        JSON,
        default=empty_json_object,
    )
    repair_count: Mapped[int] = mapped_column(Integer, default=0)
    attempt_count: Mapped[int] = mapped_column(Integer, default=0)
    model_call_count: Mapped[int] = mapped_column(Integer, default=0)
    tool_call_count: Mapped[int] = mapped_column(Integer, default=0)
    current_artifact_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    result_artifact_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    result_group_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    warning_codes_json: Mapped[list[Any]] = mapped_column(
        JSON,
        default=empty_json_array,
    )
    error_json: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    started_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    finished_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )


class JobInput(Base):
    __tablename__ = "job_inputs"
    __table_args__ = (
        UniqueConstraint(
            "job_id",
            "input_kind",
            "input_id",
            name="uq_job_inputs_job_kind_id",
        ),
        Index("ix_job_inputs_job_ordinal", "job_id", "ordinal"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    job_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("jobs.id", ondelete="CASCADE"),
    )
    input_kind: Mapped[str] = mapped_column(String(16))
    input_id: Mapped[str] = mapped_column(String(36))
    role: Mapped[str] = mapped_column(String(32))
    ordinal: Mapped[int] = mapped_column(Integer)
    frozen_sha256: Mapped[str] = mapped_column(String(64))
    metadata_json: Mapped[dict[str, Any]] = mapped_column(
        JSON,
        default=empty_json_object,
    )


class JobDependency(Base):
    __tablename__ = "job_dependencies"

    job_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("jobs.id", ondelete="CASCADE"),
        primary_key=True,
    )
    depends_on_job_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("jobs.id", ondelete="CASCADE"),
        primary_key=True,
    )
    required_status: Mapped[str] = mapped_column(
        String(64),
        default="published_success_or_warning",
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)


class JobAttempt(Base):
    __tablename__ = "job_attempts"
    __table_args__ = (
        UniqueConstraint("job_id", "attempt_no", name="uq_job_attempts_job_attempt_no"),
        Index("ix_job_attempts_job_started_at", "job_id", "started_at"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    job_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("jobs.id", ondelete="CASCADE"),
    )
    attempt_no: Mapped[int] = mapped_column(Integer)
    status: Mapped[str] = mapped_column(String(32), default="running")
    model_call_count: Mapped[int] = mapped_column(Integer, default=0)
    tool_call_count: Mapped[int] = mapped_column(Integer, default=0)
    error_json: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    finished_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )


class ToolInvocation(Base):
    __tablename__ = "tool_invocations"
    __table_args__ = (
        Index("ix_tool_invocations_job_created_at", "job_id", "created_at"),
        UniqueConstraint(
            "job_attempt_id",
            "attempt",
            name="uq_tool_invocations_attempt_sequence",
        ),
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
    job_attempt_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("job_attempts.id", ondelete="CASCADE"),
    )
    tool_name: Mapped[str] = mapped_column(String(200))
    tool_version: Mapped[int] = mapped_column(Integer)
    attempt: Mapped[int] = mapped_column(Integer)
    request_json: Mapped[dict[str, Any]] = mapped_column(
        JSON,
        default=empty_json_object,
    )
    result_json: Mapped[dict[str, Any]] = mapped_column(
        JSON,
        default=empty_json_object,
    )
    status: Mapped[str] = mapped_column(String(32), default="running")
    duration_ms: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)


class ValidationResult(Base):
    __tablename__ = "validation_results"
    __table_args__ = (
        Index("ix_validation_results_job_created_at", "job_id", "created_at"),
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
    job_attempt_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("job_attempts.id", ondelete="CASCADE"),
    )
    artifact_id: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey("artifacts.id", ondelete="CASCADE"),
        nullable=True,
    )
    validator: Mapped[str] = mapped_column(String(200))
    status: Mapped[str] = mapped_column(String(32))
    severity: Mapped[str] = mapped_column(String(16))
    summary: Mapped[str] = mapped_column(Text)
    evidence_json: Mapped[dict[str, Any]] = mapped_column(
        JSON,
        default=empty_json_object,
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)


class ModelInvocation(Base):
    __tablename__ = "model_invocations"
    __table_args__ = (
        Index("ix_model_invocations_task_created_at", "task_id", "created_at"),
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
    job_attempt_id: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey("job_attempts.id", ondelete="CASCADE"),
        nullable=True,
    )
    role: Mapped[str] = mapped_column(String(32))
    provider: Mapped[str] = mapped_column(String(100))
    model: Mapped[str] = mapped_column(String(200))
    status: Mapped[str] = mapped_column(String(32))
    prompt_tokens: Mapped[int | None] = mapped_column(Integer, nullable=True)
    output_tokens: Mapped[int | None] = mapped_column(Integer, nullable=True)
    latency_ms: Mapped[int] = mapped_column(Integer)
    error_code: Mapped[str | None] = mapped_column(String(100), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
