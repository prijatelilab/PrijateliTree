import os
from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

import prijateli_tree.app.database as models
from prijateli_tree.app.config import config
from prijateli_tree.app.utils.constants import KEY_ENV


SQL_ALCHEMY_URL = "sqlalchemy.url"
app_config = config[os.getenv(KEY_ENV)]


config = context.config
config.set_main_option(
    SQL_ALCHEMY_URL,
    app_config.SQLALCHEMY_DATABASE_URI,
)

fileConfig(config.config_file_name)

target_metadata = models.Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in `offline` mode."""
    context.configure(
        url=config.get_main_option(SQL_ALCHEMY_URL),
        target_metadata=target_metadata,
        literal_binds=True,
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in `online` mode."""
    configuration = config.get_section(config.config_ini_section)
    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
