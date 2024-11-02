import uuid
from unittest.mock import AsyncMock

from application.auth.dao import UserDao
from application.core.responses import BAD_REQUEST, NOT_FOUND, SUCCESS
from firebase.notification import NotificationEvent, get_notification_message
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from utils import get_token_need_type, rows


class TestSendFriendRequest:
    async def test_want_become_friend(
        self, _create_standard_user, _mock_prepare_notification: AsyncMock, ac: AsyncClient, session: AsyncSession
    ):
        """Тест. Отправить запрос на дружбу от пользователя А -> B"""
        usr = _create_standard_user.to_dict()
        usr.pop("password")
        second_usr = await UserDao.add_one(session, rows[1])

        response = await ac.post(
            f"/users/friend/add/{second_usr.id}",
            headers={"Authorization": f"Bearer {get_token_need_type(usr.get('id'))}"},
        )
        assert response.status_code == list(SUCCESS.keys())[0]
        _mock_prepare_notification.delay.assert_called_once_with(
            usr,
            second_usr.id,
            NotificationEvent.FRIEND_REQUEST,
            get_notification_message(NotificationEvent.FRIEND_REQUEST, usr.get("nickname")),
        )
        assert response.json() == {
            "sender": str(usr.get("id")),
            "recipient": str(second_usr.id),
            "msg": "The friendship request has been sent. After confirmation, " "you will become friends!",
        }

    async def test_resending_request(self, _create_standard_user, ac: AsyncClient, session: AsyncSession):
        """Тест. Повторная отправка запроса на дружбу"""
        usr = _create_standard_user.to_dict()
        usr.pop("password")
        second_usr = await UserDao.add_one(session, rows[1])

        await ac.post(
            f"/users/friend/add/{second_usr.id}",
            headers={"Authorization": f"Bearer {get_token_need_type(usr.get('id'))}"},
        )
        response = await ac.post(
            f"/users/friend/add/{second_usr.id}",
            headers={"Authorization": f"Bearer {get_token_need_type(usr.get('id'))}"},
        )
        assert response.status_code == list(BAD_REQUEST.keys())[0]
        assert response.json() == {
            "detail": "Such a request has already been sent earlier or you have been blocked. "
            "Duplicates not allowed."
        }

    async def test_user_not_found(self, _create_standard_user, ac: AsyncClient):
        """Тест. Нет пользователя с таким ID"""
        resp = await ac.post(
            f"/users/friend/add/{uuid.uuid4()}",
            headers={"Authorization": f"Bearer {get_token_need_type(_create_standard_user.id)}"},
        )
        assert resp.status_code == list(NOT_FOUND.keys())[0]
        assert resp.json() == {"detail": "User not found"}

    async def test_request_to_yourself(self, _create_standard_user, ac: AsyncClient):
        """Тест. Хочу дружить сам с собой?!"""
        resp = await ac.post(
            f"/users/friend/add/{_create_standard_user.id}",
            headers={"Authorization": f"Bearer {get_token_need_type(_create_standard_user.id)}"},
        )
        assert resp.status_code == list(BAD_REQUEST.keys())[0]
        assert resp.json() == {"detail": "You can't make request to yourself."}
