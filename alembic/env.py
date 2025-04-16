import asyncio
from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import AsyncEngine

from app.config import settings
from app.db.base import Base
from app.models import pet, user  


config = context.config


if config.config_file_name is not None:
    fileConfig(config.config_file_name)


target_metadata = Base.metadata


config.set_main_option("sqlalchemy.url", str(settings.SQLALCHEMY_DATABASE_URI))


def run_migrations_offline() -> None:
    """
    Запускает миграции в 'оффлайн' режиме.

    Этот метод позволяет не подключаться к базе данных при запуске миграций.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    """
    Выполняет миграции в "онлайн" режиме с предоставленным соединением.
    """
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    """
    Запускает миграции в 'онлайн' режиме.

    В этом режиме мы сначала подключаемся к базе данных, а затем запускаем миграции.
    """
    connectable = AsyncEngine(
        engine_from_config(
            config.get_section(config.config_ini_section),
            prefix="sqlalchemy.",
            poolclass=pool.NullPool,
        )
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())