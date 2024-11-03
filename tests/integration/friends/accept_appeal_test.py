from unittest.mock import AsyncMock

from application.auth.dao import UserDao
from application.core.responses import FORBIDDEN, NOT_FOUND, SUCCESS
from application.friends.models import Friend, Relations
from firebase.notification import NotificationEvent, get_notification_message
from httpx import AsyncClient
from sqlalchemy import insert
from sqlalchemy.ext.asyncio import AsyncSession
from utils import get_token_need_type, rows


class TestApproveFriendRequest:
    async def test_income_appeal(
        self, _create_standard_user, _mock_prepare_notification: AsyncMock, ac: AsyncClient, session: AsyncSession
    ):
        """Тест. Принять входящий запрос"""
        usr = _create_standard_user.to_dict()
        usr.pop("password")
        second_usr = await UserDao.add_one(session, rows[1])
        await ac.post(
            f'/users/friend/add/{usr.get("id")}',
            headers={"Authorization": f"Bearer {get_token_need_type(second_usr.id)}"},
        )
        resp = await ac.patch(
            f"/users/friend/accept/{second_usr.id}",
            headers={"Authorization": f"Bearer {get_token_need_type(usr.get('id'))}"},
        )
        _mock_prepare_notification.delay.assert_called_with(
            usr,
            second_usr.id,
            NotificationEvent.APPROVE_APPEAL,
            get_notification_message(NotificationEvent.APPROVE_APPEAL, usr.get("nickname")),
        )
        assert resp.status_code == list(SUCCESS.keys())[0]
        assert resp.json() == {"friend_id": str(second_usr.id), "msg": "You become friends!"}

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
        usr = _create_standard_user.to_dict()
        second_usr = await UserDao.add_one(session, rows[1])
        s_usr_id = second_usr.id

        stmt = insert(Friend).values(
            {"user_id": usr.get("id"), "friend_id": s_usr_id, "relationship_type": Relations.FRIEND}
        )
        await session.execute(stmt)
        await session.commit()

        resp = await ac.patch(
            f"/users/friend/accept/{s_usr_id}",
            headers={"Authorization": f"Bearer {get_token_need_type(usr.get('id'))}"},
        )
        assert resp.status_code == list(FORBIDDEN.keys())[0]
        assert resp.json() == {
            "detail": "The application status is different from NOT_APPEAL. You are either already friends or "
            "you have been blocked."
        }
