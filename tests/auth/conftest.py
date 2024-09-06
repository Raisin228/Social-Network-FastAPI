import asyncio
import uuid

import pytest
from application.auth.constants import ACCESS_TOKEN_TYPE, REFRESH_TOKEN_TYPE
from application.auth.dao import UserDao
from auth.auth import create_jwt_token
from auth.hashing_password import hash_password
from sqlalchemy.ext.asyncio import AsyncSession

USER_DATA = {
    "email": "testuser@example.com",
    "password": "very_strong_user_password123",
}

UNIQ_ID = uuid.uuid4()


@pytest.fixture(scope="function")
async def _create_standard_user(session: AsyncSession):
    """Создание пользователя перед тестом и удаления после теста."""
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
async def get_access_token(user_id: uuid.UUID = UNIQ_ID) -> str:
    """Получить access токен для конкретного user"""
    data = {"user_id": str(user_id)}
    return create_jwt_token(data, token_type=ACCESS_TOKEN_TYPE)


def get_refresh_token(user_id: uuid.UUID = UNIQ_ID, is_incorrect: bool = False) -> str:
    """Получить refresh токен для конкретного user"""
    data = {"some_info": "lalala"} if is_incorrect else {"user_id": str(user_id)}
    return create_jwt_token(data, token_type=REFRESH_TOKEN_TYPE)


@pytest.fixture(scope="session")
def event_loop():
    """Create and provide a new event loop per test."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()
