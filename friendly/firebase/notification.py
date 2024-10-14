from typing import Union
from uuid import UUID

from application.auth.models import User
from application.notifications.dao import FirebaseDeviceTokenDao
from sqlalchemy.ext.asyncio import AsyncSession


async def firebase_send_notification(
    sender: User, recipient_id: UUID, header: Union[str, None], info: Union[str, None], session: AsyncSession
):
    """Отправить уведомление от A => B"""
    # data = {"sender": sender.id, "recipient": recipient_id, "title": header, "text": info}
    # await NotificationDao.add_one(session, data)

    await FirebaseDeviceTokenDao.user_tokens(session, recipient_id)
