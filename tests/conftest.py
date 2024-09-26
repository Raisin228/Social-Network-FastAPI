import asyncio
from typing import AsyncGenerator
from unittest.mock import AsyncMock, patch

import pytest
from application.auth.dao import UserDao
from auth.hashing_password import hash_password
from config import settings
from database import Base, get_async_session
from fastapi_mail import FastMail
from httpx import ASGITransport, AsyncClient
from main import app
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from utils import UNIQ_ID, USER_DATA, get_token_need_type

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


@pytest.fixture(scope="session")
def event_loop():
    """Create and provide a new event loop per test."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
async def _create_standard_user(session: AsyncSession):
    """Создание пользователя перед тестом и удаления после теста. Фикстура"""
    new_user = await UserDao.add_one(
        session,
        {
            "id": UNIQ_ID,
            "nickname": f"id_{UNIQ_ID}",
            "email": USER_DATA["email"],
            "password": hash_password(USER_DATA["password"]),
        },
    )
    yield new_user
    await UserDao.delete_by_filter(session, {"id": new_user.id})


@pytest.fixture(scope="function")
async def get_access_token():
    """Получить access токен для конкретного user. Фикстура"""
    return get_token_need_type()


@pytest.fixture()
def _mock_send_message() -> AsyncMock:
    """Замокать ф-ию отправки сообщения на почту"""
    with patch.object(FastMail, "send_message", new_callable=AsyncMock) as mock_method:
        yield mock_method
