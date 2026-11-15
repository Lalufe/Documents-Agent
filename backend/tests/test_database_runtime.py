# pyright: basic

from pathlib import Path

from app.infrastructure.db.engine import create_engine_for_path
from sqlalchemy import text


def test_sqlite_connection_enables_required_pragmas(tmp_path: Path) -> None:
    engine = create_engine_for_path(tmp_path / "app.db")

    with engine.connect() as connection:
        assert connection.execute(text("PRAGMA journal_mode")).scalar_one() == "wal"
        assert connection.execute(text("PRAGMA foreign_keys")).scalar_one() == 1
        assert connection.execute(text("PRAGMA busy_timeout")).scalar_one() == 5000
        assert connection.execute(text("PRAGMA synchronous")).scalar_one() == 1
