# pyright: basic

import pytest
from app.api.schemas.events import (
    ExecutionEvent,
    JobStatusEvent,
    JobStatusEventData,
    TaskQueuedEvent,
    TaskQueuedEventData,
)
from pydantic import TypeAdapter


def test_event_union_selects_concrete_event_by_type() -> None:
    adapter: TypeAdapter[ExecutionEvent] = TypeAdapter(ExecutionEvent)
    event = adapter.validate_python(
        {
            "seq": 1,
            "type": "task.queued",
            "task_id": "9f2a3dc2-4b76-4f5f-b8ee-5b04e79573ee",
            "turn_id": None,
            "job_id": None,
            "timestamp": "2026-11-15T00:00:00Z",
            "data": {"queue_position": 0},
        }
    )

    assert isinstance(event, TaskQueuedEvent)
    assert isinstance(event.data, TaskQueuedEventData)
    assert event.type == "task.queued"


def test_event_union_selects_job_status_event() -> None:
    adapter: TypeAdapter[ExecutionEvent] = TypeAdapter(ExecutionEvent)
    event = adapter.validate_python(
        {
            "seq": 2,
            "type": "job.status",
            "task_id": "9f2a3dc2-4b76-4f5f-b8ee-5b04e79573ee",
            "turn_id": "c604b25f-bd97-42f5-8c56-e5cc115a468f",
            "job_id": "b20b4dcc-5883-4bab-824c-09737d72d9f0",
            "timestamp": "2026-11-15T00:00:01Z",
            "data": {"status": "converting", "dependency_state": "ready"},
        }
    )

    assert isinstance(event, JobStatusEvent)
    assert isinstance(event.data, JobStatusEventData)
    assert event.data.status.value == "converting"


def test_event_union_rejects_unknown_event_type() -> None:
    with pytest.raises(ValueError):
        TypeAdapter(ExecutionEvent).validate_python(
            {
                "seq": 1,
                "type": "unknown.event",
                "task_id": "9f2a3dc2-4b76-4f5f-b8ee-5b04e79573ee",
                "turn_id": None,
                "job_id": None,
                "timestamp": "2026-11-15T00:00:00Z",
                "data": {},
            }
        )
