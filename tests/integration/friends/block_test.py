import uuid
from unittest.mock import AsyncMock

from application.core.responses import BAD_REQUEST, FORBIDDEN, NOT_FOUND, SUCCESS
from application.friends.dao import FriendDao
from application.friends.models import Relations
from firebase.notification import NotificationEvent, get_notification_message
from httpx import AsyncClient
from integration.friends.conftest import get_two_users
from sqlalchemy.ext.asyncio import AsyncSession
from utils import get_token_need_type


class TestBlockingUser:
    async def test_add_blacklist_foreign(
        self, _create_standard_user, _mock_prepare_notification: AsyncMock, ac: AsyncClient, session: AsyncSession
    ):
        """Тест. Добавить пользователя в blacklist, с которым мы не имеем записей"""
        store = await get_two_users(_create_standard_user, session)

        resp = await ac.put(
            f"/users/ban_user/{store[1].get('id')}",
            headers={"Authorization": f"Bearer {get_token_need_type(store[0].get('id'))}"},
        )
        _mock_prepare_notification.delay.assert_called_with(
            store[0],
            store[1].get("id"),
            NotificationEvent.BAN,
            get_notification_message(NotificationEvent.BAN, store[0].get("nickname")),
        )
        assert resp.status_code == list(SUCCESS.keys())[0]
        assert resp.json() == {"msg": "This user has been added to blacklist", "block_user_id": str(store[1].get("id"))}

    async def test_add_to_black_list_familiar(
        self, _create_standard_user, _mock_prepare_notification: AsyncMock, ac: AsyncClient, session: AsyncSession
    ):
        """Тест. Блокируем знакомого (уже есть запись в Friend)"""
        store = await get_two_users(_create_standard_user, session)
        await FriendDao.friend_request(
            session,
            {"user_id": store[1].get("id"), "friend_id": store[0].get("id"), "relationship_type": Relations.FRIEND},
        )

        resp = await ac.put(
            f"/users/ban_user/{store[1].get('id')}",
            headers={"Authorization": f"Bearer {get_token_need_type(store[0].get('id'))}"},
        )
        assert resp.status_code == list(SUCCESS.keys())[0]
        assert resp.json() == {"msg": "This user has been added to blacklist", "block_user_id": str(store[1].get("id"))}

    async def test_already_block_by_this_user(self, _create_standard_user, ac: AsyncClient, session: AsyncSession):
        """Тест. Пользователь, которого мы хотим блокнуть уже это сделал"""
        store = await get_two_users(_create_standard_user, session)
        await FriendDao.friend_request(
            session,
            {"user_id": store[1].get("id"), "friend_id": store[0].get("id"), "relationship_type": Relations.BLOCKED},
        )

        resp = await ac.put(
            f"/users/ban_user/{store[1].get('id')}",
            headers={"Authorization": f"Bearer {get_token_need_type(store[0].get('id'))}"},
        )
        assert resp.status_code == list(FORBIDDEN.keys())[0]
        assert resp.json() == {"detail": "This user blocked you. You can't block someone who blocked you."}

    async def test_unblock_blocked_user(
        self, _create_standard_user, _mock_prepare_notification: AsyncMock, ac: AsyncClient, session: AsyncSession
    ):
        """Тест. Разблокировать пользователя из чёрного списка"""
        store = await get_two_users(_create_standard_user, session)
        await FriendDao.friend_request(
            session,
            {"user_id": store[0].get("id"), "friend_id": store[1].get("id"), "relationship_type": Relations.BLOCKED},
        )

        resp = await ac.put(
            f"/users/ban_user/{store[1].get('id')}",
            headers={"Authorization": f"Bearer {get_token_need_type(store[0].get('id'))}"},
        )
        _mock_prepare_notification.delay.assert_called_with(
            store[0],
            store[1].get("id"),
            NotificationEvent.BLOCK_TERMINATE,
            get_notification_message(NotificationEvent.BLOCK_TERMINATE, store[0].get("nickname")),
        )
        assert resp.status_code == list(SUCCESS.keys())[0]
        assert resp.json() == {
            "msg": "This user has been removed from the blacklist.",
            "block_user_id": str(store[1].get("id")),
        }

    async def test_banish_yourself(self, _create_standard_user, ac: AsyncClient):
        """Тест. Мы пытаемся забанить самого себя"""
        resp = await ac.put(
            f"/users/ban_user/{_create_standard_user.id}",
            headers={"Authorization": f"Bearer {get_token_need_type(_create_standard_user.id)}"},
        )
        assert resp.status_code == list(BAD_REQUEST.keys())[0]
        assert resp.json() == {"detail": "You can't make request to yourself."}

    async def test_ban_user_doesnt_exist(self, _create_standard_user, ac: AsyncClient):
        """Тест. Блокировка несуществующего в системе пользователя"""
        resp = await ac.put(
            f"/users/ban_user/{uuid.uuid4()}",
            headers={"Authorization": f"Bearer {get_token_need_type(_create_standard_user.id)}"},
        )
        assert resp.status_code == list(NOT_FOUND.keys())[0]
        assert resp.json() == {
            "detail": "The requested data is not in the system. The user with this ID was not found."
        }
