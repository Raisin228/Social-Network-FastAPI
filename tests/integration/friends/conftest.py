from typing import Dict, Tuple
from unittest.mock import AsyncMock, patch

import pytest
from application.auth.dao import UserDao
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from utils import rows


async def get_two_users(first_standard_user, session: AsyncSession) -> Tuple[Dict, Dict]:
    """Получить 2х пользователей для тестов."""
    usr = first_standard_user.to_dict()
    usr.pop("password")
    return usr, (await UserDao.add_one(session, rows[1])).to_dict()


@pytest.fixture()
def _mock_prepare_notification() -> AsyncMock:
    """Заглушка отправки push-уведомления через FireBase"""
    with patch("application.friends.router.prepare_notification") as mock:
        yield mock


@pytest.fixture(autouse=True)
async def setup_and_teardown(session: AsyncSession):
    """После каждого теста чистим таблицу User"""
    yield
    await session.execute(text('TRUNCATE TABLE "user" RESTART IDENTITY CASCADE;'))
    await session.commit()
