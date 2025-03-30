from typing import Dict, Tuple
from unittest.mock import AsyncMock, patch

import pytest
from application.auth.dao import UserDao
from database import Transaction
from utils import rows


@pytest.fixture()
def _mock_prepare_notification() -> AsyncMock:
    """Заглушка отправки push-уведомления через FireBase"""
    with patch("application.friends.router.prepare_notification") as mock:
        yield mock


async def get_two_users(first_standard_user) -> Tuple[Dict, Dict]:
    """Получить 2х пользователей для тестов."""
    usr = first_standard_user.to_dict()
    usr.pop("password")

    async with Transaction() as session:
        second_usr = (await UserDao.add(session, rows[1])).to_dict()
    return usr, second_usr
