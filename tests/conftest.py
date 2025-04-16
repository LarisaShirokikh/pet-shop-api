import asyncio
from typing import AsyncGenerator, Dict, Generator

import pytest
import pytest_asyncio
from fastapi import FastAPI
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

from app.api.v1.router import api_router
from app.config import settings
from app.core.security import create_access_token
from app.db.base import Base
from app.db.session import get_db
from app.main import app
import asyncpg


# Основной URL подключения к PostgreSQL (без указания базы данных)
POSTGRES_URL = "postgresql+asyncpg://postgres:postgres@db"
# URL тестовой базы данных
TEST_DB_NAME = "pet_shop_test"
SQLALCHEMY_DATABASE_URL = f"{POSTGRES_URL}/{TEST_DB_NAME}"


# Определяем event_loop с областью видимости session
@pytest.fixture(scope="session")
def event_loop():
    """Создает экземпляр цикла событий для каждой тестовой сессии."""
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session")
async def create_test_database():
    """Создает и удаляет тестовую базу данных."""
    # Подключаемся к postgres (база данных по умолчанию)
    conn = await asyncpg.connect(
        host="db",
        port=5432,
        user="postgres",
        password="postgres",
        database="postgres"
    )
    
    # Удаляем базу данных, если она существует
    try:
        await conn.execute(f'DROP DATABASE IF EXISTS {TEST_DB_NAME}')
    except Exception as e:
        print(f"Error dropping database: {e}")
    
    # Создаем новую базу данных
    try:
        await conn.execute(f'CREATE DATABASE {TEST_DB_NAME}')
    except Exception as e:
        print(f"Error creating database: {e}")
    
    await conn.close()
    
    # Возвращаем контроль тестам
    yield
    
    # Удаляем базу данных после завершения всех тестов
    conn = await asyncpg.connect(
        host="db",
        port=5432,
        user="postgres",
        password="postgres",
        database="postgres"
    )
    
    try:
        await conn.execute(f'DROP DATABASE IF EXISTS {TEST_DB_NAME}')
    except Exception as e:
        print(f"Error dropping database after tests: {e}")
    
    await conn.close()


@pytest_asyncio.fixture(scope="function")
async def db_engine(create_test_database):
    """Создает движок базы данных."""
    engine = create_async_engine(
        SQLALCHEMY_DATABASE_URL,
        poolclass=NullPool
    )
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def db_session(db_engine) -> AsyncGenerator[AsyncSession, None]:
    """Создает сессию базы данных и схемы таблиц."""
    
    # Создаем все таблицы
    async with db_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Создаем сессию
    TestingSessionLocal = sessionmaker(
        autocommit=False, 
        autoflush=False, 
        bind=db_engine, 
        class_=AsyncSession
    )
    
    async with TestingSessionLocal() as session:
        yield session
    
    # Удаляем все таблицы после тестов
    async with db_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture(scope="function")
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """
    Создает FastAPI TestClient, который использует тестовую БД.
    """
    # Переопределяем зависимость get_db для тестирования
    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client


@pytest_asyncio.fixture(scope="function")
async def superuser_token_headers(client: AsyncClient) -> Dict[str, str]:
    """
    Возвращает заголовки авторизации для суперпользователя.
    """
    # Создаем тестового суперпользователя
    await client.post(
        f"{settings.API_V1_STR}/auth/register-test-superuser",
        json={
            "email": "admin@mail.ru",
            "password": "admin123",
        },
    )
    
    # Получаем токен авторизации
    login_data = {
        "username": "admin@mail.ru",
        "password": "admin123",
    }
    response = await client.post(f"{settings.API_V1_STR}/auth/token", data=login_data)
    token = response.json()["access_token"]
    
    headers = {"Authorization": f"Bearer {token}"}
    return headers