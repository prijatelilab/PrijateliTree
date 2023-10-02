import os
from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

import prijateli_tree.app.models.database as models
from prijateli_tree.app.utils.constants import KEY_DATABASE_URI


config = context.config
config.set_main_option(
    "sqlalchemy.url",
    os.getenv(KEY_DATABASE_URI),
)

fileConfig(config.config_file_name)

target_metadata = models.Base.metadata


def get_url():
    user = os.getenv("POSTGRES_USER", "")
    password = os.getenv("POSTGRES_PASSWORD", "")
    server = os.getenv("POSTGRES_SERVER", "")
    db = os.getenv("POSTGRES_DB", "")
    port = os.getenv("POSTGRES_PORT", "")
    return f"postgresql://{user}:{password}@{server}:{port}/{db}"


def run_migrations_offline() -> None:
    """Run migrations in `offline` mode."""
    url = get_url()
    context.configure(
        url=url, target_metadata=target_metadata, literal_binds=True, compare_type=True
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in `online` mode."""
    configuration = config.get_section(config.config_ini_section)
    configuration["sqlalchemy.url"] = get_url()
    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata, compare_type=True
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
