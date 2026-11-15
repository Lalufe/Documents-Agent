from __future__ import annotations

from pathlib import Path

from alembic.config import Config
from alembic.script import ScriptDirectory
from sqlalchemy import Engine, inspect, text


class MigrationStateError(RuntimeError):
    pass


def current_database_revision(engine: Engine) -> str | None:
    with engine.connect() as connection:
        if not inspect(connection).has_table("alembic_version"):
            return None
        revisions = tuple(
            connection.execute(text("SELECT version_num FROM alembic_version")).scalars()
        )
    if len(revisions) > 1:
        raise MigrationStateError("数据库存在多个 Alembic 版本，拒绝启动")
    return revisions[0] if revisions else None


def database_head_revision(config_path: Path | None = None) -> str:
    configured_path = (
        config_path
        if config_path is not None
        else Path(__file__).resolve().parents[4] / "alembic.ini"
    )
    script = ScriptDirectory.from_config(Config(str(configured_path)))
    heads = script.get_heads()
    if len(heads) != 1:
        raise MigrationStateError("迁移历史必须恰好包含一个 head")
    return heads[0]


def check_database_migrations(
    engine: Engine,
    config_path: Path | None = None,
) -> None:
    current = current_database_revision(engine)
    head = database_head_revision(config_path)
    if current != head:
        raise MigrationStateError(
            f"数据库迁移状态不一致：current={current or 'none'}, head={head}"
        )
