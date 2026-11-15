from __future__ import annotations

from typing import Annotated, Literal
from uuid import UUID

from pydantic import AwareDatetime, Field

from app.api.schemas.common import ContractModel
from app.api.schemas.tasks import DependencyState, JobStatus, TaskStatus, TurnStatus
from app.api.schemas.uploads import SupportedFormat


class EventEnvelope(ContractModel):
    seq: int = Field(ge=1)
    task_id: UUID
    turn_id: UUID | None
    job_id: UUID | None
    timestamp: AwareDatetime


class TaskQueuedEventData(ContractModel):
    queue_position: int = Field(ge=0)


class TaskStartedEventData(ContractModel):
    worker_id: str


class PlanCreatedEventData(ContractModel):
    job_count: int = Field(ge=1, le=20)


class ClarificationRequiredEventData(ContractModel):
    clarification_id: UUID
    question: str


class JobWaitingEventData(ContractModel):
    depends_on: list[UUID]


class JobStatusEventData(ContractModel):
    status: JobStatus
    dependency_state: DependencyState


class JobBlockedEventData(ContractModel):
    blocked_reason: str


class TemplateDiagnosedEventData(ContractModel):
    inspection_id: UUID
    status: Literal["succeeded", "warning", "blocked", "failed"]


class ConversionStartedEventData(ContractModel):
    source_format: SupportedFormat
    target_format: SupportedFormat


class ConversionFinishedEventData(ContractModel):
    source_format: SupportedFormat
    target_format: SupportedFormat
    status: Literal["succeeded", "warning", "failed"]


class ToolStartedEventData(ContractModel):
    tool_name: str


class ToolFinishedEventData(ContractModel):
    tool_name: str
    status: Literal["succeeded", "warning", "failed"]
    duration_ms: int = Field(ge=0)


class ValidationFinishedEventData(ContractModel):
    validator: str
    status: Literal["passed", "warning", "failed"]


class ArtifactReadyEventData(ContractModel):
    artifact_id: UUID


class TurnFinishedEventData(ContractModel):
    turn_status: TurnStatus


class TaskFinishedEventData(ContractModel):
    task_status: TaskStatus


class HeartbeatEventData(ContractModel):
    interval_seconds: int = Field(default=15, ge=1)


class TaskQueuedEvent(EventEnvelope):
    type: Literal["task.queued"]
    data: TaskQueuedEventData


class TaskStartedEvent(EventEnvelope):
    type: Literal["task.started"]
    data: TaskStartedEventData


class PlanCreatedEvent(EventEnvelope):
    type: Literal["plan.created"]
    data: PlanCreatedEventData


class ClarificationRequiredEvent(EventEnvelope):
    type: Literal["clarification.required"]
    data: ClarificationRequiredEventData


class JobWaitingEvent(EventEnvelope):
    type: Literal["job.waiting"]
    data: JobWaitingEventData


class JobStatusEvent(EventEnvelope):
    type: Literal["job.status"]
    data: JobStatusEventData


class JobBlockedEvent(EventEnvelope):
    type: Literal["job.blocked"]
    data: JobBlockedEventData


class TemplateDiagnosedEvent(EventEnvelope):
    type: Literal["template.diagnosed"]
    data: TemplateDiagnosedEventData


class ConversionStartedEvent(EventEnvelope):
    type: Literal["conversion.started"]
    data: ConversionStartedEventData


class ConversionFinishedEvent(EventEnvelope):
    type: Literal["conversion.finished"]
    data: ConversionFinishedEventData


class ToolStartedEvent(EventEnvelope):
    type: Literal["tool.started"]
    data: ToolStartedEventData


class ToolFinishedEvent(EventEnvelope):
    type: Literal["tool.finished"]
    data: ToolFinishedEventData


class ValidationFinishedEvent(EventEnvelope):
    type: Literal["validation.finished"]
    data: ValidationFinishedEventData


class ArtifactReadyEvent(EventEnvelope):
    type: Literal["artifact.ready"]
    data: ArtifactReadyEventData


class TurnFinishedEvent(EventEnvelope):
    type: Literal["turn.finished"]
    data: TurnFinishedEventData


class TaskFinishedEvent(EventEnvelope):
    type: Literal["task.finished"]
    data: TaskFinishedEventData


class HeartbeatEvent(EventEnvelope):
    type: Literal["heartbeat"]
    data: HeartbeatEventData


EventUnion = (
    TaskQueuedEvent
    | TaskStartedEvent
    | PlanCreatedEvent
    | ClarificationRequiredEvent
    | JobWaitingEvent
    | JobStatusEvent
    | JobBlockedEvent
    | TemplateDiagnosedEvent
    | ConversionStartedEvent
    | ConversionFinishedEvent
    | ToolStartedEvent
    | ToolFinishedEvent
    | ValidationFinishedEvent
    | ArtifactReadyEvent
    | TurnFinishedEvent
    | TaskFinishedEvent
    | HeartbeatEvent
)

ExecutionEvent = Annotated[EventUnion, Field(discriminator="type")]
