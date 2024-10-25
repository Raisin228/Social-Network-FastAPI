import asyncio
from enum import StrEnum
from typing import Dict, List
from uuid import UUID

import firebase_admin
from application.notifications.dao import FirebaseDeviceTokenDao, NotificationDao
from config import settings
from database import session_factory
from firebase_admin import credentials, messaging
from firebase_admin.exceptions import FirebaseError
from logger_config import filter_traceback, log
from task_queue.celery_settings import celery

cred = credentials.Certificate(settings.FIREBASE_CONFIG_FILE)
firebase_admin.initialize_app(cred)


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


async def get_tokens_and_add_notify(s: Dict, r_id: UUID, title: str, body: str):
    async with session_factory() as session:
        recipient_devices = await FirebaseDeviceTokenDao.user_tokens(session, r_id)
        data = {"sender": s.get("id"), "recipient": r_id, "title": title, "message": body}
        await NotificationDao.add_one(session, data)
    return recipient_devices


@celery.task(name="notifications", max_retries=3)
def prepare_notification(sender: Dict, recipient_id: UUID, header: str, info: str) -> List[str]:
    """Сохранить уведомление в бд + рассылка на все устройства"""
    devices = asyncio.run(get_tokens_and_add_notify(sender, recipient_id, header, info))

    id_sent_notif = []
    for row in devices:
        token = row["device_token"]
        try:
            msg_id = send_notification(token, header, info)
            id_sent_notif.append(msg_id)
        except FirebaseError as ex:
            log.error("".join(filter_traceback(ex)))
    return id_sent_notif
