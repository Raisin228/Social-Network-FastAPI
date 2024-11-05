from unittest.mock import AsyncMock

from application.core.responses import FORBIDDEN, NOT_FOUND, SUCCESS
from application.friends.dao import FriendDao
from application.friends.models import Relations
from firebase.notification import NotificationEvent, get_notification_message
from httpx import AsyncClient
from integration.friends.conftest import get_two_users
from sqlalchemy.ext.asyncio import AsyncSession
from utils import get_token_need_type


class TestApproveFriendRequest:
    async def test_income_appeal(
        self, _create_standard_user, _mock_prepare_notification: AsyncMock, ac: AsyncClient, session: AsyncSession
    ):
        """Тест. Принять входящий запрос"""
        store = await get_two_users(_create_standard_user, session)
        await ac.post(
            f'/users/friend/add/{store[0].get("id")}',
            headers={"Authorization": f"Bearer {get_token_need_type(store[1].get('id'))}"},
        )
        resp = await ac.patch(
            f"/users/friend/accept/{store[1].get('id')}",
            headers={"Authorization": f"Bearer {get_token_need_type(store[0].get('id'))}"},
        )
        _mock_prepare_notification.delay.assert_called_with(
            store[0],
            store[1].get("id"),
            NotificationEvent.APPROVE_APPEAL,
            get_notification_message(NotificationEvent.APPROVE_APPEAL, store[0].get("nickname")),
        )
        assert resp.status_code == list(SUCCESS.keys())[0]
        assert resp.json() == {"friend_id": str(store[1].get("id")), "msg": "You become friends!"}

    async def test_appeal_doesnt_exist(self, _create_standard_user, ac: AsyncClient):
        """Принять запрос, которого не существует. Либо запрос самому себе"""
        usr = _create_standard_user.to_dict()
        resp = await ac.patch(
            f'/users/friend/accept/{usr.get("id")}',
            headers={"Authorization": f"Bearer {get_token_need_type(usr.get('id'))}"},
        )
        assert resp.status_code == list(NOT_FOUND.keys())[0]
        assert resp.json() == {"detail": "There is no active friendship application"}

    async def test_appeal_status_error(self, _create_standard_user, ac: AsyncClient, session: AsyncSession):
        """Тест. Статус заявки != NOT_APPROVE. Пользователи либо друзья, либо заблокированы"""
        store = await get_two_users(_create_standard_user, session)
        await FriendDao.friend_request(
            session,
            {"user_id": store[0].get("id"), "friend_id": store[1].get("id"), "relationship_type": Relations.FRIEND},
        )

        resp = await ac.patch(
            f"/users/friend/accept/{store[1].get('id')}",
            headers={"Authorization": f"Bearer {get_token_need_type(store[0].get('id'))}"},
        )
        assert resp.status_code == list(FORBIDDEN.keys())[0]
        assert resp.json() == {
            "detail": "The application status is different from NOT_APPEAL. You are either already friends or "
            "you have been blocked."
        }
