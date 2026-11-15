from __future__ import annotations

from typing import Any, cast

from fastapi import FastAPI
from pydantic import TypeAdapter

from app.api.errors import ErrorResponse
from app.api.schemas.events import ExecutionEvent
from app.api.schemas.tasks import ActivityPage, TaskDetail, TaskSummary
from app.api.schemas.uploads import UploadRecord


def _add_model_schema(
    components: dict[str, Any],
    model: type[object],
) -> None:
    model_schema = cast(
        dict[str, Any],
        model.model_json_schema(  # type: ignore[attr-defined]
            mode="serialization",
            ref_template="#/components/schemas/{model}",
        ),
    )
    definitions = cast(dict[str, Any], model_schema.pop("$defs", {}))
    for definition_name, definition in definitions.items():
        components.setdefault(definition_name, definition)
    components.setdefault(model.__name__, model_schema)


def _add_contract_components(schema: dict[str, Any]) -> None:
    components: dict[str, Any] = (
        schema.setdefault("components", {}).setdefault("schemas", {})
    )
    for model in (
        UploadRecord,
        TaskSummary,
        TaskDetail,
        ActivityPage,
        ErrorResponse,
    ):
        _add_model_schema(components, model)

    event_schema = TypeAdapter(ExecutionEvent).json_schema(
        mode="serialization",
        ref_template="#/components/schemas/{model}",
    )
    definitions = cast(dict[str, Any], event_schema.pop("$defs", {}))
    for definition_name, definition in definitions.items():
        components.setdefault(definition_name, definition)
    components.setdefault("ExecutionEvent", event_schema)


def install_contract_components(app: FastAPI) -> None:
    original_openapi = app.openapi

    def openapi_with_core_contracts() -> dict[str, Any]:
        if app.openapi_schema is not None:
            return app.openapi_schema
        schema = original_openapi()
        _add_contract_components(schema)
        app.openapi_schema = schema
        return schema

    app.openapi = openapi_with_core_contracts  # type: ignore[method-assign]
