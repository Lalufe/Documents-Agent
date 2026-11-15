# pyright: basic

from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from app.api.main import create_app
from app.api.schemas.common import OfficeHealth
from app.infrastructure.db.migrations import MigrationStateError
from app.settings import AppSettings
from fastapi.testclient import TestClient


def migrate(database_path: Path) -> None:
    config = Config("alembic.ini")
    config.set_main_option("script_location", "backend/migrations")
    config.set_main_option(
        "sqlalchemy.url",
        f"sqlite+pysqlite:///{database_path.as_posix()}",
    )
    command.upgrade(config, "head")


def settings_for(tmp_path: Path) -> AppSettings:
    return AppSettings.from_env(
        env={"DOC_AGENT_DATA_DIR": str(tmp_path)},
        cwd=tmp_path,
    )


def test_health_reports_configuration_and_office_dependency(
    tmp_path: Path,
) -> None:
    settings = settings_for(tmp_path)
    migrate(settings.database_path)
    app = create_app(
        settings=settings,
        office_probe=lambda: OfficeHealth(
            status="available",
            detail="registry",
        ),
    )

    with TestClient(app) as client:
        response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "application": "ok",
        "database": "ok",
        "config": "ok",
        "migrations": "ok",
        "office": {"status": "available", "detail": "registry"},
    }


def test_startup_rejects_database_without_migrations(tmp_path: Path) -> None:
    settings = settings_for(tmp_path)
    app = create_app(
        settings=settings,
        office_probe=lambda: OfficeHealth(status="unavailable", detail=None),
    )

    with pytest.raises(MigrationStateError), TestClient(app):
        pass
