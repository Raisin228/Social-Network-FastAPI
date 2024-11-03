from unittest.mock import AsyncMock

from application.auth.dao import UserDao
from application.core.responses import SUCCESS
from firebase.notification import NotificationEvent, get_notification_message
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from utils import get_token_need_type, rows


class TestBlockingUser:
    async def test_add_blacklist(
        self, _create_standard_user, _mock_prepare_notification: AsyncMock, ac: AsyncClient, session: AsyncSession
    ):
        """Тест. Добавить пользователя в blacklist"""
        usr = _create_standard_user.to_dict()
        usr.pop("password")
        second_usr = await UserDao.add_one(session, rows[1])

        resp = await ac.put(
            f"/users/ban_user/{second_usr.id}",
            headers={"Authorization": f"Bearer {get_token_need_type(usr.get('id'))}"},
        )
        _mock_prepare_notification.delay.assert_called_with(
            usr,
            second_usr.id,
            NotificationEvent.BAN,
            get_notification_message(NotificationEvent.BAN, usr.get("nickname")),
        )
        assert resp.status_code == list(SUCCESS.keys())[0]
        assert resp.json() == {"msg": "This user has been added to blacklist", "block_user_id": str(second_usr.id)}
