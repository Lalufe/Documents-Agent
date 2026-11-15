from __future__ import annotations

import os
from logging.config import fileConfig

from alembic import context
from app.infrastructure.db import models as db_models  # noqa: F401  # pyright: ignore[reportUnusedImport]
from app.infrastructure.db.base import Base
from app.infrastructure.db.engine import database_path_from_env
from sqlalchemy import engine_from_config, pool

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

if os.environ.get("DOC_AGENT_DATA_DIR"):
    database_url = f"sqlite+pysqlite:///{database_path_from_env().as_posix()}"
    config.set_main_option("sqlalchemy.url", database_url)

target_metadata = Base.metadata


def include_object(
    _object: object,
    name: str | None,
    type_: str,
    _reflected: bool,
    _compare_to: object | None,
) -> bool:
    if type_ != "table" or name is None:
        return True
    return name != "content_chunks_fts" and not name.startswith(
        "content_chunks_fts_"
    )


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        include_object=include_object,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            include_object=include_object,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
