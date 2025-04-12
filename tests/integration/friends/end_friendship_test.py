import uuid
from unittest.mock import AsyncMock

from application.core.responses import NOT_FOUND, SUCCESS
from application.friends.dao import FriendDao
from application.friends.models import Relations
from firebase.notification import NotificationEvent, get_notification_message
from httpx import AsyncClient
from integration.friends.conftest import get_two_users
from sqlalchemy.ext.asyncio import AsyncSession
from utils import get_token_need_type


class TestEndFriendshipWithUser:
    async def test_deleting_user_from_friends(
        self,
        _create_standard_user,
        _mock_prepare_notification: AsyncMock,
        ac: AsyncClient,
        session: AsyncSession,
    ):
        """Тест. Удаляем пользователя из списка друзей"""
        store = await get_two_users(_create_standard_user)
        await FriendDao.friend_request(
            session,
            {
                "user_id": store[0].get("id"),
                "friend_id": store[1].get("id"),
                "relationship_type": Relations.FRIEND,
            },
        )

        resp = await ac.delete(
            f"/users/friend/remove/{store[1].get('id')}",
            headers={"Authorization": f"Bearer {get_token_need_type(store[0].get('id'))}"},
        )
        _mock_prepare_notification.delay.assert_called_with(
            store[0],
            store[1].get("id"),
            NotificationEvent.END_FRIENDSHIP,
            get_notification_message(NotificationEvent.END_FRIENDSHIP, store[0].get("nickname")),
        )
        assert resp.status_code == list(SUCCESS.keys())[0]
        assert resp.json() == {
            "former_friend_id": str(store[1].get("id")),
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
