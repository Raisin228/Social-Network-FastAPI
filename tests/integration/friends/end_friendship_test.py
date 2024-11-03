import uuid
from unittest.mock import AsyncMock

from application.auth.dao import UserDao
from application.core.responses import NOT_FOUND, SUCCESS
from application.friends.models import Friend, Relations
from firebase.notification import NotificationEvent, get_notification_message
from httpx import AsyncClient
from sqlalchemy import insert
from sqlalchemy.ext.asyncio import AsyncSession
from utils import get_token_need_type, rows


class TestEndFriendshipWithUser:
    async def test_deleting_user_from_friends(
        self, _create_standard_user, _mock_prepare_notification: AsyncMock, ac: AsyncClient, session: AsyncSession
    ):
        """Тест. Удаляем пользователя из списка друзей"""
        usr = _create_standard_user.to_dict()
        usr.pop("password")
        second_usr = await UserDao.add_one(session, rows[1])
        s_usr_id = second_usr.id

        stmt = insert(Friend).values(
            {"user_id": usr.get("id"), "friend_id": s_usr_id, "relationship_type": Relations.FRIEND}
        )
        await session.execute(stmt)
        await session.commit()

        resp = await ac.delete(
            f"/users/friend/remove/{s_usr_id}",
            headers={"Authorization": f"Bearer {get_token_need_type(usr.get('id'))}"},
        )

        _mock_prepare_notification.delay.assert_called_with(
            usr,
            s_usr_id,
            NotificationEvent.END_FRIENDSHIP,
            get_notification_message(NotificationEvent.END_FRIENDSHIP, usr.get("nickname")),
        )
        assert resp.status_code == list(SUCCESS.keys())[0]
        assert resp.json() == {
            "former_friend_id": str(s_usr_id),
            "msg": "The user has been removed from the friends" " list",
        }

    async def test_not_friends_with(self, _create_standard_user, ac: AsyncClient):
        """Пытаемся удалить из друзей пользователя, с которым и так не дружим"""
        resp = await ac.delete(
            f"/users/friend/remove/{uuid.uuid4()}",
            headers={"Authorization": f"Bearer {get_token_need_type(_create_standard_user.id)}"},
        )

        assert resp.status_code == list(NOT_FOUND.keys())[0]
        assert resp.json() == {"detail": "You aren't friends with the user"}
