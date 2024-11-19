from typing import Dict, List, Tuple, Union
from uuid import UUID

from application.core.exceptions import DataDoesNotExist
from application.notifications.exceptions import SuchDeviceTokenAlreadyExist
from application.notifications.models import (
    FirebaseDeviceToken,
    Notification,
    NotificationStatus,
)
from data_access_object.base import BaseDAO
from sqlalchemy import case, select
from sqlalchemy.ext.asyncio import AsyncSession


class FirebaseDeviceTokenDao(BaseDAO):
    model = FirebaseDeviceToken

    @classmethod
    async def add_token(cls, session: AsyncSession, user_id: UUID, token: str) -> Union[Exception, FirebaseDeviceToken]:
        """Добавить токен (идентификатор) устройства в бд"""
        device_for_user = await FirebaseDeviceTokenDao.find_by_filter(session, {"device_token": token})
        if device_for_user is None:
            return await FirebaseDeviceTokenDao.add_one(session, {"holder_id": user_id, "device_token": token})
        raise SuchDeviceTokenAlreadyExist()

    @classmethod
    async def user_tokens(cls, session: AsyncSession, user_id: UUID) -> List[Dict]:
        """Все устройства, куда можно отправлять уведомления"""
        devices = await FirebaseDeviceTokenDao.find_by_filter(session, {"holder_id": user_id})
        if devices is None:
            return []
        return [devices] if isinstance(devices, Dict) else devices


class NotificationDao(BaseDAO):
    model = Notification

    @classmethod
    async def get_notifications(cls, offset: int, limit: int, recipient: UUID, session: AsyncSession) -> List[model]:
        """Все уведомления, отправленные пользователю"""
        query = (
            select(cls.model)
            .where(cls.model.recipient == recipient)
            .order_by(case((cls.model.status == NotificationStatus.UNREAD, 0), else_=1), cls.model.created_at.desc())
            .offset(offset)
            .limit(limit)
        )

        notifications = await session.execute(query)
        return list(notifications.scalars())

    @classmethod
    async def change_notify_status(
        cls, n_id: UUID, receiver_id: UUID, session: AsyncSession
    ) -> Union[Exception, Tuple]:
        """Изменить статус уведомления"""
        notify = await NotificationDao.find_by_filter(session, {"id": n_id, "recipient": receiver_id})
        if notify is None:
            raise DataDoesNotExist

        if notify.get("status") == NotificationStatus.UNREAD:
            new_status = NotificationStatus.READ
        else:
            new_status = NotificationStatus.UNREAD
        return (await NotificationDao.update_row(session, {"status": new_status}, {"id": n_id}))[0]
