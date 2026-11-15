from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy import (
    JSON,
    CheckConstraint,
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


class Upload(Base):
    __tablename__ = "uploads"
    __table_args__ = (Index("ix_uploads_status_expires_at", "status", "expires_at"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    original_name: Mapped[str] = mapped_column(Text)
    stored_name: Mapped[str] = mapped_column(Text)
    sha256: Mapped[str] = mapped_column(String(64))
    format: Mapped[str] = mapped_column(String(16))
    size_bytes: Mapped[int] = mapped_column(Integer)
    status: Mapped[str] = mapped_column(String(32), default="staged")
    preflight_json: Mapped[dict[str, Any]] = mapped_column(
        JSON,
        default=empty_json_object,
    )
    expires_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)


class UploadedFile(Base):
    __tablename__ = "uploaded_files"
    __table_args__ = (
        UniqueConstraint("upload_id", name="uq_uploaded_files_upload_id"),
        Index("ix_uploaded_files_task_id", "task_id"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    task_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("tasks.id", ondelete="CASCADE"),
    )
    upload_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("uploads.id", ondelete="RESTRICT"),
    )
    original_name: Mapped[str] = mapped_column(Text)
    stored_name: Mapped[str] = mapped_column(Text)
    sha256: Mapped[str] = mapped_column(String(64))
    format: Mapped[str] = mapped_column(String(16))
    size_bytes: Mapped[int] = mapped_column(Integer)
    preflight_json: Mapped[dict[str, Any]] = mapped_column(
        JSON,
        default=empty_json_object,
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)


class TemplateInspection(Base):
    __tablename__ = "template_inspections"
    __table_args__ = (
        Index(
            "ix_template_inspections_upload_status",
            "uploaded_file_id",
            "status",
        ),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    uploaded_file_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("uploaded_files.id", ondelete="CASCADE"),
    )
    format: Mapped[str] = mapped_column(String(16))
    engine_version: Mapped[int] = mapped_column(Integer)
    status: Mapped[str] = mapped_column(String(32), default="queued")
    manifest_json: Mapped[dict[str, Any]] = mapped_column(
        JSON,
        default=empty_json_object,
    )
    diagnostics_json: Mapped[list[Any]] = mapped_column(JSON)
    mapping_json: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    finished_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )


class DocumentSnapshot(Base):
    __tablename__ = "document_snapshots"
    __table_args__ = (
        CheckConstraint(
            "(artifact_id IS NOT NULL AND uploaded_file_id IS NULL) OR "
            "(artifact_id IS NULL AND uploaded_file_id IS NOT NULL)",
            name="ck_document_snapshots_exactly_one_source",
        ),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    artifact_id: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey("artifacts.id", ondelete="CASCADE"),
        unique=True,
        nullable=True,
    )
    uploaded_file_id: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey("uploaded_files.id", ondelete="CASCADE"),
        unique=True,
        nullable=True,
    )
    format: Mapped[str] = mapped_column(String(16))
    schema_version: Mapped[int] = mapped_column(Integer)
    content_hash: Mapped[str] = mapped_column(String(64))
    snapshot_path: Mapped[str] = mapped_column(Text)
    metadata_json: Mapped[dict[str, Any]] = mapped_column(
        JSON,
        default=empty_json_object,
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)


class ContentChunk(Base):
    __tablename__ = "content_chunks"
    __table_args__ = (
        UniqueConstraint(
            "snapshot_id",
            "ordinal",
            name="uq_content_chunks_snapshot_ordinal",
        ),
        Index("ix_content_chunks_snapshot_id", "snapshot_id"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    snapshot_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("document_snapshots.id", ondelete="CASCADE"),
    )
    ordinal: Mapped[int] = mapped_column(Integer)
    block_id: Mapped[str] = mapped_column(String(100))
    text: Mapped[str] = mapped_column(Text)
    search_text: Mapped[str] = mapped_column(Text)
    locator_json: Mapped[dict[str, Any]] = mapped_column(
        JSON,
        default=empty_json_object,
    )
    token_estimate: Mapped[int] = mapped_column(Integer)
