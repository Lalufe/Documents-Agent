# pyright: basic

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


def create_engine_for_database(database_path: Path):
    return create_engine(f"sqlite+pysqlite:///{database_path.as_posix()}")


def seed_task_and_turn(connection) -> None:
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


def test_initial_migration_creates_all_design_tables(tmp_path: Path) -> None:
    database_path = tmp_path / "app.db"
    upgrade_database(database_path)

    with create_engine_for_database(database_path).connect() as connection:
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
    engine = create_engine_for_database(database_path)

    with engine.begin() as connection:
        connection.execute(text("PRAGMA foreign_keys = ON"))
        seed_task_and_turn(connection)
        connection.execute(text("DELETE FROM tasks WHERE id = 'task-1'"))

    with engine.connect() as connection:
        count = connection.execute(text("SELECT COUNT(*) FROM task_turns")).scalar_one()
    assert count == 0


def test_non_null_artifact_slot_is_unique_per_turn(tmp_path: Path) -> None:
    database_path = tmp_path / "app.db"
    upgrade_database(database_path)
    engine = create_engine_for_database(database_path)

    with engine.begin() as connection:
        connection.execute(text("PRAGMA foreign_keys = ON"))
        seed_task_and_turn(connection)
        connection.execute(
            text(
                "INSERT INTO jobs "
                "(id, task_id, turn_id, plan_index, job_type, goal, status, dependency_state, "
                "artifact_slot, target_format, execution_spec_json, repair_count, attempt_count, "
                "model_call_count, tool_call_count, warning_codes_json, created_at) "
                "VALUES ('job-1', 'task-1', 'turn-1', 1, 'convert', 'c', 'planned', "
                "'waiting', 'out', 'pdf', '{}', 0, 0, 0, 0, '[]', CURRENT_TIMESTAMP)"
            )
        )

    with pytest.raises(IntegrityError), engine.begin() as connection:
        connection.execute(
            text(
                "INSERT INTO jobs "
                "(id, task_id, turn_id, plan_index, job_type, goal, status, dependency_state, "
                "artifact_slot, target_format, execution_spec_json, repair_count, "
                "attempt_count, model_call_count, tool_call_count, warning_codes_json, "
                "created_at) "
                "VALUES ('job-2', 'task-1', 'turn-1', 2, 'convert', 'c', 'planned', "
                "'waiting', 'out', 'pdf', '{}', 0, 0, 0, 0, '[]', CURRENT_TIMESTAMP)"
            )
        )


def test_document_snapshot_requires_exactly_one_source(tmp_path: Path) -> None:
    database_path = tmp_path / "app.db"
    upgrade_database(database_path)
    engine = create_engine_for_database(database_path)

    with pytest.raises(IntegrityError), engine.begin() as connection:
        connection.execute(
            text(
                "INSERT INTO document_snapshots "
                "(id, format, schema_version, content_hash, snapshot_path, "
                "metadata_json, created_at) "
                "VALUES ('snapshot-1', 'txt', 1, 'hash', 'snapshots/a.json', "
                "'{}', CURRENT_TIMESTAMP)"
            )
        )


def test_fts_table_and_triggers_exist(tmp_path: Path) -> None:
    database_path = tmp_path / "app.db"
    upgrade_database(database_path)

    with create_engine_for_database(database_path).connect() as connection:
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


def test_migrated_schema_has_no_alembic_metadata_diff(tmp_path: Path) -> None:
    database_path = tmp_path / "app.db"
    upgrade_database(database_path)
    config = Config("alembic.ini")
    config.set_main_option("script_location", "backend/migrations")
    config.set_main_option(
        "sqlalchemy.url",
        f"sqlite+pysqlite:///{database_path.as_posix()}",
    )

    command.check(config)


def test_alembic_uses_configured_data_directory(
    monkeypatch,
    tmp_path: Path,
) -> None:
    monkeypatch.setenv("DOC_AGENT_DATA_DIR", str(tmp_path))
    config = Config("alembic.ini")
    config.set_main_option("script_location", "backend/migrations")

    command.upgrade(config, "head")

    assert (tmp_path / "app.db").exists()


def test_alembic_uses_configured_database_path(
    monkeypatch,
    tmp_path: Path,
) -> None:
    monkeypatch.setenv("DOC_AGENT_DATA_DIR", str(tmp_path))
    monkeypatch.setenv("DOC_AGENT_DB_PATH", "state/custom.db")
    config = Config("alembic.ini")
    config.set_main_option("script_location", "backend/migrations")

    command.upgrade(config, "head")

    assert (tmp_path / "state" / "custom.db").exists()
