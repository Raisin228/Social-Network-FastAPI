import uuid
from typing import Dict, Tuple

import pytest
from application.core.exceptions import DataDoesNotExist
from application.core.responses import NOT_FOUND, SUCCESS
from application.notifications.dao import NotificationDao
from database import Transaction
from firebase.notification import NotificationEvent, get_notification_message
from httpx import AsyncClient
from integration.friends.conftest import get_two_users
from utils import get_token_need_type


async def make_test_notification(usr, status: str = "UNREAD") -> Tuple[Dict, Tuple[Dict, Dict]]:
    """Создаёт запись о тестовом уведомлении в бд"""
    store = await get_two_users(usr)
    msg_info = get_notification_message(NotificationEvent.BLOCK_TERMINATE, store[0].get("nickname"))
    prepared_data = {
        "sender": str(store[0].get("id")),
        "recipient": str(store[1].get("id")),
        "title": NotificationEvent.BLOCK_TERMINATE.value,
        "message": msg_info,
        "status": status,
    }
    async with Transaction() as sess:
        temp = await NotificationDao.add(sess, prepared_data)
        temp_dict = temp.to_dict()
    saved_notify = {
        key: str(value) if key in ["sender", "recipient", "id"] else value
        for key, value in temp_dict.items()
    }
    saved_notify["created_at"] = saved_notify["created_at"].isoformat()
    saved_notify.pop("recipient")
    return saved_notify, store


class TestGetListNotify:
    async def test_get_notifications(self, _create_standard_user, ac: AsyncClient):
        """Тест. Получить мои уведомления"""
        data = await make_test_notification(_create_standard_user)

        res = await ac.get(
            "/notify/notifications",
            headers={"Authorization": f"Bearer {get_token_need_type(data[1][1].get('id'))}"},
        )
        assert res.status_code == list(SUCCESS.keys())[0]
        assert res.json() == [data[0]]

    async def test_no_notifications(self, _create_standard_user, ac: AsyncClient):
        """Входящих уведомлений не найдено"""
        res = await ac.get(
            "/notify/notifications",
            headers={"Authorization": f"Bearer {get_token_need_type(_create_standard_user.id)}"},
        )
        assert res.status_code == list(NOT_FOUND.keys())[0]
        assert res.json() == {"detail": "No incoming notifications."}


class TestMarkNotifyAs:
    incorrect_dates = ["READ", "UNREAD"]

    async def test_event_dont_exist(self, _create_standard_user, ac: AsyncClient):
        """В системе нет уведомления с таким ID либо оно не принадлежит данному User"""
        res = await ac.patch(
            f"/notify/mark-notify-read/{uuid.uuid4()}",
            headers={"Authorization": f"Bearer {get_token_need_type(_create_standard_user.id)}"},
        )
        assert res.status_code == list(NOT_FOUND.keys())[0]
        assert res.json() == {
            "detail": f"{DataDoesNotExist().msg} Notifications with this"
            f" ID don't exist in the system."
        }

    @pytest.mark.parametrize("stat", incorrect_dates)
    async def test_change_status(self, stat: str, _create_standard_user, ac: AsyncClient):
        """Меняем статус у записи"""
        data = await make_test_notification(_create_standard_user, stat)
        data[0]["status"] = "READ" if stat == "UNREAD" else "UNREAD"

        res = await ac.patch(
            f'/notify/mark-notify-read/{data[0].get("id")}',
            headers={"Authorization": f"Bearer {get_token_need_type(data[1][1].get('id'))}"},
        )
        assert res.status_code == list(SUCCESS.keys())[0]
        assert res.json() == data[0]


class TestDeleteNot:
    async def test_nothing_delete(self, _create_standard_user, ac: AsyncClient):
        """Хотим удалить уведомления, которых нет"""
        res = await ac.delete(
            "/notify/clear-notifications",
            headers={"Authorization": f"Bearer {get_token_need_type(_create_standard_user.id)}"},
        )
        assert res.status_code == list(NOT_FOUND.keys())[0]
        assert res.json() == {"detail": "No incoming notifications."}

    async def test_clear_all_incoming(self, _create_standard_user, ac: AsyncClient):
        """Удалить все входящие"""
        data = await make_test_notification(_create_standard_user)

        res = await ac.delete(
            "/notify/clear-notifications",
            headers={"Authorization": f"Bearer {get_token_need_type(data[1][1].get('id'))}"},
        )
        assert res.status_code == list(SUCCESS.keys())[0]
        assert res.json() == {"msg": "Successful delete", "notify_removed": 1}
