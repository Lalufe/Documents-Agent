# BE1 M0 Foundation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Deliver T01-T03 as a runnable FastAPI/React foundation with versioned Pydantic contracts, an exported OpenAPI document, and a migrated SQLite schema.

**Architecture:** Use one installable Python project rooted at the repository root, with source code under `backend/app`, and a minimal Vite frontend under `frontend`. Build contracts independently from persistence, then connect both through a minimal FastAPI application while keeping upload, task services, SSE transport, and worker behavior out of this milestone.

**Tech Stack:** Python 3.11, uv, FastAPI, Pydantic 2, SQLAlchemy 2, Alembic, SQLite, Pytest, HTTPX, Ruff, Pyright, React, TypeScript, Vite, pnpm.

**Spec:** `docs/superpowers/specs/2026-11-15-be1-m0-foundation-design.md`

## Global Constraints

- Python version is `>=3.11,<3.12`.
- API base path is `/api/v1`.
- IDs use UUID strings; timestamps use UTC ISO 8601.
- Error responses contain exactly the core fields `code`, `message`, `details`, and `request_id`.
- Lists use cursor pagination.
- SQLite connections set `journal_mode=WAL`, `foreign_keys=ON`, `busy_timeout=5000`, and `synchronous=NORMAL`.
- All schema changes go through Alembic.
- Business foreign keys use `ON DELETE CASCADE`.
- `data` contains no committed database, log, staging, task, snapshot, preview, or artifact files.
- T01-T03 do not implement upload endpoints, task services, SSE transport, worker behavior, Office checks, or later BE1 tasks.
- GitHub Flow is mandatory: work on `feat/be1-m0-foundation`, commit each task separately, push the branch, and open a PR to `master`.

---

### Task 1: T01 Project Skeleton

**Files:**
- Create: `.gitignore`
- Create: `.env.example`
- Create: `pyproject.toml`
- Create: `backend/app/__init__.py`
- Create: `backend/app/api/__init__.py`
- Create: `backend/app/api/main.py`
- Create: `backend/app/application/__init__.py`
- Create: `backend/app/infrastructure/__init__.py`
- Create: `backend/app/worker/__init__.py`
- Create: `backend/tests/__init__.py`
- Create: `backend/tests/test_bootstrap.py`
- Create: `backend/pytest.ini`
- Create: `frontend/package.json`
- Create: `frontend/tsconfig.json`
- Create: `frontend/vite.config.ts`
- Create: `frontend/index.html`
- Create: `frontend/src/main.tsx`
- Create: `frontend/src/App.tsx`
- Create: `frontend/src/vite-env.d.ts`
- Create: `data/.gitkeep`
- Create: `scripts/contracts/.gitkeep`

**Interfaces:**
- Consumes: no earlier task.
- Produces: `app.api.main.create_app() -> FastAPI` and `app.api.main.app: FastAPI`.
- Produces: pnpm scripts `typecheck` and `build` in `frontend/package.json`.

- [x] **Step 1: Write the failing bootstrap test**

```python
# backend/tests/test_bootstrap.py
from fastapi import FastAPI


def test_create_app_returns_fastapi_application() -> None:
    from app.api.main import create_app

    app = create_app()

    assert isinstance(app, FastAPI)
    assert app.title == "文档处理办公 Agent API"
    assert app.docs_url == "/docs"
```

- [x] **Step 2: Run the test to verify it fails**

Run: `uv run pytest backend/tests/test_bootstrap.py -v`

Expected: collection fails because the root package configuration or `app.api.main` does not exist.

- [x] **Step 3: Add the Python and frontend package skeleton**

Create `pyproject.toml` with:

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "doc-agent"
version = "0.1.0"
description = "Local multi-format document processing and office agent"
requires-python = ">=3.11,<3.12"
dependencies = [
  "alembic>=1.16,<2",
  "fastapi>=0.116,<1",
  "pydantic>=2.11,<3",
  "sqlalchemy>=2.0.41,<3",
  "uvicorn[standard]>=0.35,<1",
]

[dependency-groups]
dev = [
  "httpx>=0.28,<1",
  "pyright>=1.1.403,<2",
  "pytest>=8.4,<9",
  "pytest-asyncio>=1.1,<2",
  "ruff>=0.12,<1",
]

[tool.hatch.build.targets.wheel]
packages = ["backend/app"]

[tool.pytest.ini_options]
testpaths = ["backend/tests"]
pythonpath = ["backend"]

[tool.ruff]
target-version = "py311"
line-length = 100

[tool.ruff.lint]
select = ["E", "F", "I", "UP", "B", "SIM"]

[tool.pyright]
include = ["backend/app", "backend/tests"]
pythonVersion = "3.11"
typeCheckingMode = "strict"
```

Create a minimal `create_app()` implementation and module-level `app = create_app()` in `backend/app/api/main.py`. The title must be `文档处理办公 Agent API` and docs URL must be `/docs`.

Create a minimal Vite React entry point and TypeScript files. `frontend/package.json` must include these scripts:

```json
{
  "scripts": {
    "build": "vite build",
    "typecheck": "tsc --noEmit"
  }
}
```

Include `react`, `react-dom`, `vite`, `typescript`, `@types/react`, and `@types/react-dom` as dependencies. The root element may render the static product name, with no feature UI.

Create `.gitignore` covering:

```text
.venv/
__pycache__/
*.py[cod]
.pytest_cache/
.ruff_cache/
.superpowers/
node_modules/
frontend/dist/
data/*
!data/.gitkeep
*.db
*.db-wal
*.db-shm
.env
```

Create `.env.example`:

```dotenv
DOC_AGENT_DATA_DIR=./data
DOC_AGENT_API_HOST=127.0.0.1
DOC_AGENT_API_PORT=8000
```

- [x] **Step 4: Install dependencies and run the bootstrap checks**

Run: `uv sync`

Run: `pnpm --dir frontend install`

Run: `uv run pytest backend/tests/test_bootstrap.py -v`

Run: `pnpm --dir frontend typecheck`

Run: `pnpm --dir frontend build`

Expected: all commands exit with code 0.

- [x] **Step 5: Commit T01**

```powershell
git add .gitignore .env.example pyproject.toml uv.lock backend frontend data scripts
git commit -m "feat: scaffold BE1 application foundation"
```

---

### Task 2: T02 HTTP and Event Contracts

**Files:**
- Create: `backend/app/api/errors.py`
- Create: `backend/app/api/schemas/__init__.py`
- Create: `backend/app/api/schemas/common.py`
- Create: `backend/app/api/schemas/uploads.py`
- Create: `backend/app/api/schemas/tasks.py`
- Create: `backend/app/api/schemas/events.py`
- Create: `backend/app/api/routes/__init__.py`
- Create: `backend/app/api/routes/health.py`
- Create: `backend/app/api/routes/contracts.py`
- Modify: `backend/app/api/main.py`
- Create: `backend/tests/test_contracts_common.py`
- Create: `backend/tests/test_contracts_events.py`
- Create: `backend/tests/test_api.py`
- Create: `scripts/contracts/export_openapi.py`
- Create: `backend/openapi.json`

**Interfaces:**
- Consumes: `create_app() -> FastAPI` from Task 1.
- Produces: `ErrorCode`, `ErrorResponse`, `AppError`, and `install_exception_handlers(app: FastAPI) -> None`.
- Produces: `CursorPage[T]` with `items: list[T]`, `next_cursor: str | None`, and `has_more: bool`.
- Produces: `ExecutionEvent` as a discriminated union keyed by `type`.
- Produces: `GET /health`, `GET /api/v1/openapi.json`, and `scripts.contracts.export_openapi.export_openapi(path: Path) -> None`.

- [x] **Step 1: Write failing common contract tests**

```python
# backend/tests/test_contracts_common.py
from uuid import UUID

import pytest
from pydantic import ValidationError

from app.api.errors import ErrorCode, ErrorResponse
from app.api.schemas.common import CursorPage
from app.api.schemas.tasks import TaskSummary


def test_error_response_has_required_contract_fields() -> None:
    response = ErrorResponse(
        code=ErrorCode.PATH_FORBIDDEN,
        message="路径不允许",
        details={"field": "path"},
        request_id="9f2a3dc2-4b76-4f5f-b8ee-5b04e79573ee",
    )

    assert response.model_dump(mode="json") == {
        "code": "PATH_FORBIDDEN",
        "message": "路径不允许",
        "details": {"field": "path"},
        "request_id": "9f2a3dc2-4b76-4f5f-b8ee-5b04e79573ee",
    }


def test_cursor_page_rejects_extra_fields() -> None:
    with pytest.raises(ValidationError):
        CursorPage[TaskSummary].model_validate(
            {"items": [], "next_cursor": None, "has_more": False, "total": 0}
        )


def test_task_id_is_uuid() -> None:
    summary = TaskSummary.model_validate(
        {
            "task_id": "9f2a3dc2-4b76-4f5f-b8ee-5b04e79573ee",
            "title": "读取报告",
            "status": "queued",
            "created_at": "2026-11-15T00:00:00Z",
            "updated_at": "2026-11-15T00:00:00Z",
        }
    )

    assert isinstance(summary.task_id, UUID)
```

- [x] **Step 2: Run the common contract tests to verify they fail**

Run: `uv run pytest backend/tests/test_contracts_common.py -v`

Expected: collection fails because the error and schema modules do not exist.

- [x] **Step 3: Implement common, error, upload, and task contracts**

`ErrorCode` must be a `StrEnum` containing every code from `Design.md` section 9.9. `ErrorResponse` uses `ConfigDict(extra="forbid")`.

`AppError` must expose:

```python
class AppError(Exception):
    def __init__(
        self,
        code: ErrorCode,
        message: str,
        *,
        status_code: int = 400,
        details: dict[str, object] | None = None,
    ) -> None: ...
```

`install_exception_handlers(app: FastAPI) -> None` must add or generate a request ID, return `ErrorResponse`, and set `X-Request-ID` on both success and error responses.

Implement these core enums in their owning schema modules:

- Task status values from `Design.md` section 10.2.
- Turn status values from section 10.3.
- Job status and dependency state values from section 10.6.
- Upload status values from section 10.5.
- Artifact kind and state values from section 10.10.
- Message roles from section 10.4.
- Event severity values from section 10.14.

Implement DTOs with UUID IDs, timezone-aware datetimes, and `extra="forbid"`:

- `UploadPreflight`, `UploadRecord`
- `FileRole`, `OutputHint`, `CreateTaskRequest`, `CreateTurnRequest`, `BaseRef`
- `TaskSummary`, `TaskDetail`, `TurnSummary`, `JobSummary`
- `ResultGroupSummary`, `ArtifactSummary`

- [x] **Step 4: Run the common contract tests to verify they pass**

Run: `uv run pytest backend/tests/test_contracts_common.py -v`

Expected: all tests pass.

- [x] **Step 5: Write failing SSE union and API tests**

```python
# backend/tests/test_contracts_events.py
from datetime import UTC, datetime
from typing import cast

import pytest
from pydantic import TypeAdapter

from app.api.schemas.events import ExecutionEvent, JobStatusEventData, TaskQueuedEventData


def test_event_union_selects_concrete_event_by_type() -> None:
    adapter = TypeAdapter(ExecutionEvent)
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

    assert isinstance(event.data, TaskQueuedEventData)
    assert event.type == "task.queued"


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
```

Create one concrete event model and event-data model for every event name in the spec. Validate the concrete event class type with the union's `TypeAdapter`.

```python
# backend/tests/test_api.py
from fastapi.testclient import TestClient

from app.api.main import app


def test_health_reports_application_status() -> None:
    response = TestClient(app).get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert response.json()["database"] == "ok"
    assert response.headers["X-Request-ID"]


def test_openapi_endpoint_exports_core_schemas() -> None:
    response = TestClient(app).get("/api/v1/openapi.json")

    assert response.status_code == 200
    schema = response.json()
    assert schema["info"]["title"] == "文档处理办公 Agent API"
    assert "ErrorResponse" in schema["components"]["schemas"]
    assert "TaskDetail" in schema["components"]["schemas"]
```

- [x] **Step 6: Run SSE and API tests to verify they fail**

Run: `uv run pytest backend/tests/test_contracts_events.py backend/tests/test_api.py -v`

Expected: failures because the event union, routers, and exception handlers are not implemented.

- [x] **Step 7: Implement routers, SSE union, middleware, and OpenAPI export**

The event envelope uses:

```python
class EventEnvelope(BaseModel):
    model_config = ConfigDict(extra="forbid")

    seq: int = Field(ge=1)
    task_id: UUID
    turn_id: UUID | None
    job_id: UUID | None
    timestamp: datetime
```

Each concrete event has a literal `type` and a concrete event-data model. The final `ExecutionEvent` is a union of concrete classes annotated with `Field(discriminator="type")`.

Implement `/health` to return:

```json
{
  "status": "ok",
  "database": "ok",
  "application": "ok"
}
```

The handler must add a request ID and `X-Request-ID` header. The initial database status is `ok` while T03 introduces the engine; T03 updates the handler to execute `SELECT 1`.

Implement request middleware that preserves an incoming `X-Request-ID` when it is a valid UUID and otherwise generates a new UUID. Store the request ID in `request.state.request_id`.

Implement `scripts/contracts/export_openapi.py` with a deterministic JSON writer:

```python
def export_openapi(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    content = json.dumps(app.openapi(), ensure_ascii=False, indent=2, sort_keys=True)
    path.write_text(content + "\n", encoding="utf-8", newline="\n")
```

- [x] **Step 8: Run the API and contract tests to verify they pass**

Run: `uv run pytest backend/tests -v`

Expected: all tests pass.

- [x] **Step 9: Export OpenAPI and verify it is deterministic**

Run: `uv run python -m scripts.contracts.export_openapi`

Run: `git add backend/openapi.json`

Run: `uv run python -m scripts.contracts.export_openapi`

Run: `git diff --exit-code -- backend/openapi.json`

Expected: the second export produces no diff.

- [x] **Step 10: Commit T02**

```powershell
git add backend/app/api backend/tests scripts backend/openapi.json
git commit -m "feat: define BE1 API and event contracts"
```

---

### Task 3: T03 SQLAlchemy Models and Alembic Migration

**Files:**
- Create: `backend/app/infrastructure/db/__init__.py`
- Create: `backend/app/infrastructure/db/base.py`
- Create: `backend/app/infrastructure/db/engine.py`
- Create: `backend/app/infrastructure/db/models/__init__.py`
- Create: `backend/app/infrastructure/db/models/task.py`
- Create: `backend/app/infrastructure/db/models/upload.py`
- Create: `backend/app/infrastructure/db/models/job.py`
- Create: `backend/app/infrastructure/db/models/artifact.py`
- Create: `backend/app/infrastructure/db/models/event.py`
- Create: `backend/app/infrastructure/db/models/idempotency.py`
- Create: `backend/app/infrastructure/db/session.py`
- Create: `alembic.ini`
- Create: `backend/migrations/env.py`
- Create: `backend/migrations/script.py.mako`
- Create: `backend/migrations/versions/20261115_0001_initial_schema.py`
- Modify: `backend/app/api/main.py`
- Create: `backend/tests/test_database_runtime.py`
- Create: `backend/tests/test_migrations.py`

**Interfaces:**
- Consumes: `create_app()` and `/health` from Tasks 1-2.
- Produces: `Base` declarative base and all ORM model classes.
- Produces: `create_engine_for_path(database_path: Path) -> Engine`, `create_session_factory(engine: Engine) -> sessionmaker[Session]`, and `get_session() -> Iterator[Session]`.
- Produces: `backend/app/infrastructure/db/models/__init__.py` that imports every model so Alembic metadata is complete.

- [x] **Step 1: Write failing database runtime tests**

```python
# backend/tests/test_database_runtime.py
from pathlib import Path

from sqlalchemy import text

from app.infrastructure.db.engine import create_engine_for_path


def test_sqlite_connection_enables_required_pragmas(tmp_path: Path) -> None:
    engine = create_engine_for_path(tmp_path / "app.db")

    with engine.connect() as connection:
        assert connection.execute(text("PRAGMA journal_mode")).scalar_one() == "wal"
        assert connection.execute(text("PRAGMA foreign_keys")).scalar_one() == 1
        assert connection.execute(text("PRAGMA busy_timeout")).scalar_one() == 5000
        assert connection.execute(text("PRAGMA synchronous")).scalar_one() == 1
```

- [x] **Step 2: Run the runtime test to verify it fails**

Run: `uv run pytest backend/tests/test_database_runtime.py -v`

Expected: collection fails because `app.infrastructure.db.engine` does not exist.

- [x] **Step 3: Implement the database base, engine, and session factory**

`base.py` defines:

```python
class Base(DeclarativeBase):
    pass
```

`engine.py` creates SQLite engines and registers a `connect` event listener. The listener executes:

```sql
PRAGMA journal_mode = WAL;
PRAGMA foreign_keys = ON;
PRAGMA busy_timeout = 5000;
PRAGMA synchronous = NORMAL;
```

`session.py` provides an `expire_on_commit=False` session factory and an iterator dependency that rolls back on exceptions and always closes the session.

- [x] **Step 4: Run the runtime test to verify it passes**

Run: `uv run pytest backend/tests/test_database_runtime.py -v`

Expected: pass.

- [x] **Step 5: Write failing migration and constraint tests**

```python
# backend/tests/test_migrations.py
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.exc import IntegrityError


def upgrade_database(database_path: Path) -> None:
    config = Config("alembic.ini")
    config.set_main_option("script_location", "backend/migrations")
    config.set_main_option(
        "sqlalchemy.url",
        f"sqlite+pysqlite:///{database_path.as_posix()}",
    )
    command.upgrade(config, "head")


def test_initial_migration_creates_all_design_tables(tmp_path: Path) -> None:
    database_path = tmp_path / "app.db"
    upgrade_database(database_path)

    with create_engine(f"sqlite+pysqlite:///{database_path.as_posix()}").connect() as connection:
        tables = set(inspect(connection).get_table_names())

    assert {
        "tasks",
        "task_turns",
        "messages",
        "uploads",
        "uploaded_files",
        "jobs",
        "job_inputs",
        "job_dependencies",
        "job_attempts",
        "template_inspections",
        "result_groups",
        "artifacts",
        "document_snapshots",
        "content_chunks",
        "content_chunks_fts",
        "clarifications",
        "execution_events",
        "tool_invocations",
        "validation_results",
        "model_invocations",
        "idempotency_keys",
    }.issubset(tables)


def test_task_delete_cascades_to_turns(tmp_path: Path) -> None:
    database_path = tmp_path / "app.db"
    upgrade_database(database_path)
    engine = create_engine(f"sqlite+pysqlite:///{database_path.as_posix()}")

    with engine.begin() as connection:
        connection.execute(text("PRAGMA foreign_keys = ON"))
        connection.execute(
            text(
                "INSERT INTO tasks "
                "(id, title, status, aggregate_json, created_at, updated_at) "
                "VALUES (:id, 't', 'queued', '{}', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)"
            ),
            {"id": "task-1"},
        )
        connection.execute(
            text(
                "INSERT INTO task_turns "
                "(id, task_id, sequence, instruction, task_kinds, status, "
                "constraints_json, created_at) "
                "VALUES ('turn-1', 'task-1', 1, 'read', '[]', 'queued', '{}', CURRENT_TIMESTAMP)"
            )
        )
        connection.execute(text("DELETE FROM tasks WHERE id = 'task-1'"))

    with engine.connect() as connection:
        count = connection.execute(text("SELECT COUNT(*) FROM task_turns")).scalar_one()
    assert count == 0


def test_non_null_artifact_slot_is_unique_per_turn(tmp_path: Path) -> None:
    database_path = tmp_path / "app.db"
    upgrade_database(database_path)
    engine = create_engine(f"sqlite+pysqlite:///{database_path.as_posix()}")

    with engine.begin() as connection:
        connection.execute(text("PRAGMA foreign_keys = ON"))
        connection.execute(
            text(
                "INSERT INTO tasks "
                "(id, title, status, aggregate_json, created_at, updated_at) "
                "VALUES ('task-1', 't', 'queued', '{}', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)"
            )
        )
        connection.execute(
            text(
                "INSERT INTO task_turns "
                "(id, task_id, sequence, instruction, task_kinds, status, "
                "constraints_json, created_at) "
                "VALUES ('turn-1', 'task-1', 1, 'read', '[]', 'queued', '{}', CURRENT_TIMESTAMP)"
            )
        )
        common = (
            "INSERT INTO jobs "
            "(id, task_id, turn_id, plan_index, job_type, goal, status, dependency_state, "
            "artifact_slot, target_format, execution_spec_json, repair_count, attempt_count, "
            "model_call_count, tool_call_count, warning_codes_json, created_at) "
            "VALUES (:id, 'task-1', 'turn-1', :plan_index, 'convert', 'c', 'planned', "
            "'waiting', 'out', 'pdf', '{}', 0, 0, 0, 0, '[]', CURRENT_TIMESTAMP)"
        )
        connection.execute(text(common), {"id": "job-1", "plan_index": 1})

    with pytest.raises(IntegrityError):
        with engine.begin() as connection:
            connection.execute(text(common), {"id": "job-2", "plan_index": 2})


def test_fts_table_and_triggers_exist(tmp_path: Path) -> None:
    database_path = tmp_path / "app.db"
    upgrade_database(database_path)

    with create_engine(f"sqlite+pysqlite:///{database_path.as_posix()}").connect() as connection:
        trigger_names = {
            row[0]
            for row in connection.execute(
                text("SELECT name FROM sqlite_master WHERE type = 'trigger'")
            )
        }

    assert {
        "content_chunks_ai",
        "content_chunks_ad",
        "content_chunks_au",
    }.issubset(trigger_names)
```

- [x] **Step 6: Run migration tests to verify they fail**

Run: `uv run pytest backend/tests/test_migrations.py -v`

Expected: failures because Alembic configuration, models, and migration revision do not exist.

- [x] **Step 7: Implement all SQLAlchemy models**

Create model classes for every table from `Design.md` sections 10.2-10.18. Use `String(36)` UUID primary keys, `JSON` for JSON columns, timezone-aware `DateTime(timezone=True)`, and `ondelete="CASCADE"` for business foreign keys.

Required constraints:

- `task_turns` unique `(task_id, sequence)`.
- partial unique index on non-null `(turn_id, artifact_slot)`.
- unique `(job_id, input_kind, input_id)` on `job_inputs`.
- `job_dependencies` composite primary key.
- unique `result_groups.job_id`.
- check constraint ensuring `document_snapshots` has exactly one source reference.
- indexes listed in `Design.md` section 10.

Import every model in `models/__init__.py` and set Alembic `target_metadata = Base.metadata`.

- [x] **Step 8: Configure Alembic, generate the initial revision, and add FTS**

Create root `alembic.ini` with `script_location = %(here)s/backend/migrations` and an overridden `sqlalchemy.url`. The root location preserves the documented `uv run alembic upgrade head` command.

Generate the initial revision:

```powershell
uv run alembic revision --autogenerate -m "initial schema" --rev-id 20261115_0001
```

Inspect the generated migration and ensure every table, foreign key, unique constraint, check constraint, and index appears explicitly. Rename the revision file to `backend/migrations/versions/20261115_0001_initial_schema.py`.

Append explicit SQL operations for the external-content FTS table and triggers:

```sql
CREATE VIRTUAL TABLE content_chunks_fts USING fts5(
    search_text,
    content='content_chunks',
    content_rowid='rowid',
    tokenize='trigram'
);

CREATE TRIGGER content_chunks_ai AFTER INSERT ON content_chunks BEGIN
    INSERT INTO content_chunks_fts(rowid, search_text)
    VALUES (new.rowid, new.search_text);
END;

CREATE TRIGGER content_chunks_ad AFTER DELETE ON content_chunks BEGIN
    INSERT INTO content_chunks_fts(content_chunks_fts, rowid, search_text)
    VALUES ('delete', old.rowid, old.search_text);
END;

CREATE TRIGGER content_chunks_au AFTER UPDATE ON content_chunks BEGIN
    INSERT INTO content_chunks_fts(content_chunks_fts, rowid, search_text)
    VALUES ('delete', old.rowid, old.search_text);
    INSERT INTO content_chunks_fts(rowid, search_text)
    VALUES (new.rowid, new.search_text);
END;
```

The downgrade drops triggers and the FTS table before dropping ordinary tables.

- [x] **Step 9: Connect `/health` to the database**

Resolve `DOC_AGENT_DATA_DIR`, default to `./data`, create the directory, resolve the database path under that root, and lazily create the engine. `/health` executes `SELECT 1`. If the database check fails, return status 503 with `database: "error"` while preserving the standard error response contract for API errors.

- [x] **Step 10: Run the migration and database tests to verify they pass**

Run: `uv run pytest backend/tests/test_database_runtime.py backend/tests/test_migrations.py -v`

Expected: all tests pass.

- [x] **Step 11: Run the full backend suite**

Run: `uv run pytest backend/tests -v`

Expected: all tests pass.

- [x] **Step 12: Commit T03**

```powershell
git add backend/app/infrastructure/db backend/app/api/main.py alembic.ini backend/migrations backend/tests
git commit -m "feat: add SQLite schema and migrations"
```

---

### Task 4: Verification and GitHub Flow Delivery

**Files:**
- Modify only files needed to resolve verification failures.
- Create: no additional product files.

**Interfaces:**
- Consumes: completed T01-T03.
- Produces: verified feature branch and a pull request targeting `master`.

- [x] **Step 1: Run the complete quality gate**

Run: `uv run ruff check .`

Run: `uv run pyright backend`

Run: `uv run pytest`

Run: `uv run alembic upgrade head`

Run: `pnpm --dir frontend typecheck`

Run: `pnpm --dir frontend build`

Run: `uv run python -m scripts.contracts.export_openapi`

Run: `git diff --exit-code -- backend/openapi.json`

Expected: every command exits with code 0 and the OpenAPI export produces no diff.

- [x] **Step 2: Verify the migration from an empty data directory**

Run:

```powershell
$tempData = Join-Path $env:TEMP ("doc-agent-" + [guid]::NewGuid())
$env:DOC_AGENT_DATA_DIR = $tempData
uv run alembic upgrade head
Test-Path (Join-Path $tempData "app.db")
```

Expected: both the migration and file existence check succeed.

- [x] **Step 3: Review the branch diff and ensure no generated or sensitive files are staged**

Run: `git status --short`

Run: `git diff --stat origin/master...HEAD`

Expected: no database, data file, log, frontend build output, `.env`, or `.superpowers` content is tracked.

- [ ] **Step 4: Push the feature branch**

Run: `git push -u origin feat/be1-m0-foundation`

Expected: the branch is available on `origin`.

- [ ] **Step 5: Open the pull request**

Run:

```powershell
gh pr create --base master --head feat/be1-m0-foundation --title "feat: complete BE1 M0 foundation" --body "Implements BE1 T01-T03: project skeleton, API contracts, OpenAPI export, SQLAlchemy models, SQLite configuration, and Alembic initial migration. Verification: Ruff, Pyright, Pytest, Alembic upgrade, frontend typecheck, frontend build, and deterministic OpenAPI export."
```

Expected: GitHub returns the pull request URL.
