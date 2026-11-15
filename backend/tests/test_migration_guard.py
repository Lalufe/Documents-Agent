# pyright: basic

from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from app.infrastructure.db.migrations import (
    MigrationStateError,
    check_database_migrations,
    current_database_revision,
)
from sqlalchemy import create_engine


def database_engine(database_path: Path):
    return create_engine(f"sqlite+pysqlite:///{database_path.as_posix()}")


def upgrade(database_path: Path) -> None:
    config = Config("alembic.ini")
    config.set_main_option("script_location", "backend/migrations")
    config.set_main_option(
        "sqlalchemy.url",
        f"sqlite+pysqlite:///{database_path.as_posix()}",
    )
    command.upgrade(config, "head")


def test_unmigrated_database_is_rejected(tmp_path: Path) -> None:
    engine = database_engine(tmp_path / "empty.db")

    assert current_database_revision(engine) is None
    with pytest.raises(MigrationStateError):
        check_database_migrations(engine)


def test_current_database_passes_migration_guard(tmp_path: Path) -> None:
    database_path = tmp_path / "current.db"
    upgrade(database_path)
    engine = database_engine(database_path)

    assert current_database_revision(engine) == "20261115_0001"
    check_database_migrations(engine)
