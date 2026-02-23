from logging.config import fileConfig
import os
from dotenv import load_dotenv

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

# 1. Загружаем переменные окружения (.env)
load_dotenv()

# 2. Импортируем твой Base для доступа к метаданным моделей
from bot.database.models import Base

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# 3. ПОДКЛЮЧАЕМ МЕТАДАННЫЕ (Было: target_metadata = None)
# Теперь Alembic увидит все таблицы, описанные в моделях наследующих Base
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    # Берем URL из env, если нет - из конфига
    url = os.getenv("DATABASE_URL")
    
    if not url:
        raise ValueError("No database URL found! Set DATABASE_URL in .env")

    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    # 1. Получаем URL из переменной окружения
    db_url = os.getenv("DATABASE_URL")
    
    if not db_url:
        db_url = config.get_main_option("sqlalchemy.url")

    if not db_url:
        raise ValueError("No database URL found!")

    # 2. ВАЖНО: Заменяем asyncpg на psycopg2 для Alembic
    # Alembic не поддерживает асинхронные драйверы напрямую
    if db_url.startswith("postgresql+asyncpg://"):
        db_url = db_url.replace("postgresql+asyncpg://", "postgresql+psycopg2://")
    
    # Принудительно устанавливаем исправленный URL в конфиг
    config.set_main_option("sqlalchemy.url", db_url)

    # Дальше всё как было
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, 
            target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()