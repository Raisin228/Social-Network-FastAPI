from typing import AsyncGenerator

import pytest
from config import settings
from database import Base, get_async_session
from httpx import ASGITransport, AsyncClient
from main import app
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

test_async_engine = create_async_engine(url=settings.db_url_for_test, echo=False, pool_size=5, max_overflow=10)

test_session_factory = async_sessionmaker(test_async_engine, class_=AsyncSession)
Base.metadata.bind = test_async_engine


async def override_get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """Переопределение подключения к бд для session = Depends"""
    async with test_session_factory() as session:
        yield session


app.dependency_overrides[get_async_session] = override_get_async_session


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
        await connection.run_sync(Base.metadata.create_all)
    yield
    async with test_async_engine.begin() as connection:
        await connection.run_sync(Base.metadata.drop_all)
