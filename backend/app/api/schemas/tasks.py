from __future__ import annotations

from enum import StrEnum
from typing import Literal
from uuid import UUID

from pydantic import AwareDatetime, Field, JsonValue

from app.api.schemas.common import ContractModel
from app.api.schemas.uploads import FileRole, SupportedFormat, UploadedFileSummary


class TaskStatus(StrEnum):
    QUEUED = "queued"
    RUNNING = "running"
    WAITING_DEPENDENCY = "waiting_dependency"
    VALIDATING = "validating"
    REPAIRING = "repairing"
    AWAITING_CLARIFICATION = "awaiting_clarification"
    SUCCEEDED = "succeeded"
    PARTIAL_SUCCESS = "partial_success"
    WARNING = "warning"
    FAILED = "failed"
    INTERRUPTED = "interrupted"
    DELETING = "deleting"


class TurnStatus(StrEnum):
    QUEUED = "queued"
    PLANNING = "planning"
    AWAITING_CLARIFICATION = "awaiting_clarification"
    RUNNING = "running"
    WAITING_DEPENDENCY = "waiting_dependency"
    VALIDATING = "validating"
    REPAIRING = "repairing"
    SUCCEEDED = "succeeded"
    PARTIAL_SUCCESS = "partial_success"
    WARNING = "warning"
    FAILED = "failed"
    INTERRUPTED = "interrupted"
    CANCELLED = "cancelled"


class TaskKind(StrEnum):
    READ = "read"
    EDIT = "edit"
    CONVERT = "convert"
    IMAGE_COMPOSE = "image_compose"
    TEMPLATE_GENERATE = "template_generate"
    GENERATE_FROM_SCRATCH = "generate_from_scratch"


class JobType(StrEnum):
    READ = "read"
    EDIT = "edit"
    CONVERT = "convert"
    TEMPLATE_GENERATE = "template_generate"
    GENERATE_FROM_SCRATCH = "generate_from_scratch"
    IMAGE_COMPOSE = "image_compose"


class JobStatus(StrEnum):
    PLANNED = "planned"
    WAITING_DEPENDENCY = "waiting_dependency"
    ANALYZING = "analyzing"
    PROFILING_TEMPLATE = "profiling_template"
    CONVERTING = "converting"
    GENERATING = "generating"
    MODIFYING = "modifying"
    VALIDATING = "validating"
    REPAIRING = "repairing"
    SUCCEEDED = "succeeded"
    WARNING = "warning"
    FAILED = "failed"
    BLOCKED = "blocked"
    INTERRUPTED = "interrupted"


class DependencyState(StrEnum):
    READY = "ready"
    WAITING = "waiting"
    BLOCKED = "blocked"


class MessageRole(StrEnum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM_NOTICE = "system_notice"


class ArtifactKind(StrEnum):
    WORKING = "working"
    INTERMEDIATE = "intermediate"
    RESULT = "result"
    PREVIEW = "preview"
    PAGE_IMAGE = "page_image"
    EXPORT = "export"


class ArtifactState(StrEnum):
    STAGED = "staged"
    PUBLISHED = "published"
    FAILED = "failed"
    DELETED = "deleted"


class OutputHint(ContractModel):
    format: SupportedFormat
    label: str = Field(min_length=1, max_length=200)


class JobInputRef(ContractModel):
    kind: Literal["upload", "artifact"]
    id: UUID
    role: FileRole
    ordinal: int = Field(ge=0)


class BaseRef(ContractModel):
    kind: Literal["artifact", "uploaded_file"]
    id: UUID


class CreateTaskRequest(ContractModel):
    upload_ids: list[UUID] = Field(default_factory=list[UUID], max_length=10)
    instruction: str = Field(min_length=1, max_length=8000)
    output_hints: list[OutputHint] = Field(default_factory=list[OutputHint])


class CreateTurnRequest(ContractModel):
    instruction: str = Field(min_length=1, max_length=8000)
    base_refs: list[BaseRef] = Field(default_factory=list[BaseRef])


class ArtifactSummary(ContractModel):
    artifact_id: UUID
    job_id: UUID | None
    kind: ArtifactKind
    format: SupportedFormat
    sha256: str
    size_bytes: int = Field(ge=0)
    state: ArtifactState
    published_at: AwareDatetime | None


class ResultGroupSummary(ContractModel):
    result_group_id: UUID
    job_id: UUID
    target_format: SupportedFormat
    label: str
    artifact_ids: list[UUID] = Field(default_factory=list[UUID])
    state: ArtifactState


class JobSummary(ContractModel):
    job_id: UUID
    job_type: JobType
    goal: str
    status: JobStatus
    depends_on: list[UUID] = Field(default_factory=list[UUID])
    input_refs: list[JobInputRef] = Field(default_factory=list[JobInputRef])
    target_format: SupportedFormat | None = None
    dependency_state: DependencyState
    result_artifact_id: UUID | None = None
    result_group_id: UUID | None = None
    result_artifact_ids: list[UUID] = Field(default_factory=list[UUID])
    warnings: list[str] = Field(default_factory=list[str])
    blocked_reason: str | None = None


class TurnSummary(ContractModel):
    turn_id: UUID
    sequence: int = Field(ge=1)
    instruction: str
    task_kinds: list[TaskKind] = Field(default_factory=list[TaskKind])
    status: TurnStatus
    created_at: AwareDatetime
    started_at: AwareDatetime | None = None
    finished_at: AwareDatetime | None = None


class EventPreview(ContractModel):
    event_id: int = Field(ge=1)
    type: str
    message: str
    severity: str
    created_at: AwareDatetime


class TaskSummary(ContractModel):
    task_id: UUID
    title: str
    status: TaskStatus
    created_at: AwareDatetime
    updated_at: AwareDatetime


class TaskDetail(ContractModel):
    task_id: UUID
    title: str
    status: TaskStatus
    current_turn_id: UUID | None
    aggregate: dict[str, JsonValue]
    turns: list[TurnSummary] = Field(default_factory=list[TurnSummary])
    jobs: list[JobSummary] = Field(default_factory=list[JobSummary])
    uploaded_files: list[UploadedFileSummary] = Field(
        default_factory=list[UploadedFileSummary]
    )
    artifacts: list[ArtifactSummary] = Field(default_factory=list[ArtifactSummary])
    result_groups: list[ResultGroupSummary] = Field(
        default_factory=list[ResultGroupSummary]
    )
    recent_events: list[EventPreview] = Field(default_factory=list[EventPreview])
    created_at: AwareDatetime
    updated_at: AwareDatetime
    started_at: AwareDatetime | None = None
    finished_at: AwareDatetime | None = None


class ActivityPage(ContractModel):
    message: str
