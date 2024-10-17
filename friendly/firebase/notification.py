from enum import StrEnum
from typing import List
from uuid import UUID

from application.auth.models import User
from application.notifications.dao import FirebaseDeviceTokenDao, NotificationDao
from firebase_admin import messaging
from firebase_admin.exceptions import FirebaseError
from sqlalchemy.ext.asyncio import AsyncSession


class NotificationEvent(StrEnum):
    """Всевозможные события для уведомлений"""

    FRIEND_REQUEST = "Новая заявка в друзья"
    APPROVE_APPEAL = "Одобрена заявка"
    BAN = "Вас заблокировали"
    BLOCK_TERMINATE = "Блокировка прекращена"
    END_FRIENDSHIP = "Дружба прекращена"


def get_notification_message(event_type: NotificationEvent, nick: str) -> str:
    """Сообщение для уведомления"""
    notify_event_msg = {
        NotificationEvent.FRIEND_REQUEST: f"Пользователь [{nick}] хочет добавить вас в друзья.",
        NotificationEvent.APPROVE_APPEAL: f"Пользователь [{nick}] принял ваш запрос. Теперь вы друзья.",
        NotificationEvent.BLOCK_TERMINATE: f"Пользователь [{nick}] удалил вас из чёрного списка. Начните общение!",
        NotificationEvent.BAN: f"Пользователь [{nick}] добавил вас в чёрный список.",
        NotificationEvent.END_FRIENDSHIP: f"Пользователь [{nick}] удалил вас из списка друзей",
    }
    return notify_event_msg.get(event_type, "Неизвестное событие")


def send_notification(device_token: str, title: str, body: str) -> str:
    """Отправить уведомление от A => B"""
    message = messaging.Message(notification=messaging.Notification(title=title, body=body), token=device_token)
    return messaging.send(message)


# TODO добавить отправку уведомлений через background task
async def prepare_notification(
    sender: User, recipient_id: UUID, session: AsyncSession, header: str, info: str
) -> List[str]:
    """Сохранить уведомление в бд + рассылка на все устройства"""
    recipient_devices = await FirebaseDeviceTokenDao.user_tokens(session, recipient_id)

    data = {"sender": sender.id, "recipient": recipient_id, "title": header, "message": info}
    await NotificationDao.add_one(session, data)

    id_sent_notif = []
    for row in recipient_devices:
        token = row["device_token"]
        try:
            msg_id = send_notification(token, header, info)
            id_sent_notif.append(msg_id)
        except FirebaseError:
            # TODO добавить логирование?
            ...
    return id_sent_notif
