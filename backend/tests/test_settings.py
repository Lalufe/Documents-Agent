# pyright: basic

from pathlib import Path

import pytest
from app.infrastructure.paths import PathForbiddenError, resolve_relative_path
from app.settings import AppSettings, ConfigurationError


def test_settings_resolve_database_inside_data_root(tmp_path: Path) -> None:
    settings = AppSettings.from_env(
        env={
            "DOC_AGENT_DATA_DIR": str(tmp_path),
            "DOC_AGENT_DB_PATH": "state/app.db",
        },
        cwd=tmp_path,
    )

    assert settings.data_dir == tmp_path.resolve()
    assert settings.database_path == (tmp_path / "state" / "app.db").resolve()
    assert (tmp_path / "tasks").is_dir()
    assert (tmp_path / "staging").is_dir()
    assert (tmp_path / "logs").is_dir()


def test_settings_reject_database_outside_data_root(tmp_path: Path) -> None:
    outside = tmp_path.parent / "outside.db"

    with pytest.raises(PathForbiddenError):
        AppSettings.from_env(
            env={
                "DOC_AGENT_DATA_DIR": str(tmp_path),
                "DOC_AGENT_DB_PATH": str(outside),
            },
            cwd=tmp_path,
        )


def test_relative_path_guard_rejects_parent_traversal(tmp_path: Path) -> None:
    with pytest.raises(PathForbiddenError):
        resolve_relative_path(tmp_path, "../escape.txt")


def test_relative_path_guard_rejects_absolute_paths_even_inside_root(
    tmp_path: Path,
) -> None:
    with pytest.raises(PathForbiddenError):
        resolve_relative_path(tmp_path, str(tmp_path / "inside.txt"))


def test_relative_path_guard_accepts_nested_path(tmp_path: Path) -> None:
    resolved = resolve_relative_path(tmp_path, "tasks/task-1/input/report.txt")

    assert resolved == (tmp_path / "tasks/task-1/input/report.txt").resolve()


def test_settings_reject_invalid_timeout(tmp_path: Path) -> None:
    with pytest.raises(ConfigurationError):
        AppSettings.from_env(
            env={
                "DOC_AGENT_DATA_DIR": str(tmp_path),
                "DOC_AGENT_TASK_TIMEOUT_SECONDS": "0",
            },
            cwd=tmp_path,
        )
