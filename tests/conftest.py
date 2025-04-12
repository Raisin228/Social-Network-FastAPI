import asyncio
from typing import AsyncGenerator
from unittest.mock import patch

import database
import fakeredis
import pytest
from application.auth.models import User
from config import settings
from httpx import ASGITransport, AsyncClient
from main import app
from redis_service import RedisService
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from utils import get_token_need_type, rows

test_async_engine = create_async_engine(
    url=settings.db_url_for_test, echo=False, pool_size=5, max_overflow=10
)

test_session_factory = async_sessionmaker(test_async_engine, class_=AsyncSession)
database.Base.metadata.bind = test_async_engine

database.session_factory = test_session_factory


async def override_get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """Переопределение подключения к бд для session = Depends"""
    async with test_session_factory() as session:
        yield session


app.dependency_overrides[database.get_async_session] = override_get_async_session


@pytest.fixture(scope="session")
async def session():
    """Получение асинхронной сессии"""
    async with test_session_factory() as session:
        yield session


@pytest.fixture(scope="session")
async def ac() -> AsyncGenerator[AsyncClient, None]:
    """Асинхронный клиент для выполнения запросов"""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac


@pytest.fixture(autouse=True, scope="session")
async def prepare_database():
    """Создание и удаление тестовой DB перед запуском тестов"""
    async with test_async_engine.begin() as connection:
        await connection.run_sync(database.Base.metadata.create_all)
    yield
    async with test_async_engine.begin() as connection:
        await connection.run_sync(database.Base.metadata.drop_all)


@pytest.fixture(autouse=True, scope="session")
async def replace_redis_by_fakeredis():
    """Заменяем действительный сервер Redis на FakeRedis"""
    test_redis_client = fakeredis.aioredis.FakeRedis()
    with patch.object(RedisService, "async_client", test_redis_client):
        yield
    await test_redis_client.close()


@pytest.fixture(scope="session")
def event_loop():
    """Create and provide a new event loop per test."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
async def _create_standard_user(session: AsyncSession) -> User:
    """Создание пользователя перед тестом и удаления после теста. Фикстура"""
    info = rows[0]
    data = User(**info)
    session.add(data)
    await session.commit()
    await session.refresh(data)
    yield data
    await session.delete(data)
    await session.commit()


@pytest.fixture(scope="function")
async def get_access_token():
    """Получить access токен для конкретного user. Фикстура"""
    return get_token_need_type()


@pytest.fixture(autouse=True)
async def setup_and_teardown(session: AsyncSession):
    """После каждого теста чистим таблицу User"""
    yield
    await session.execute(text('TRUNCATE TABLE "user" RESTART IDENTITY CASCADE;'))
    await session.commit()
