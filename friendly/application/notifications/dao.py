from typing import Union
from uuid import UUID

from application.core.exceptions import SuchDeviceTokenAlreadyExist
from application.notifications.models import FirebaseDeviceToken
from data_access_object.base import BaseDAO
from sqlalchemy.ext.asyncio import AsyncSession


class FirebaseDeviceTokenDao(BaseDAO):
    model = FirebaseDeviceToken

    @classmethod
    async def add_token(cls, session: AsyncSession, user_id: UUID, token: str) -> Union[Exception, FirebaseDeviceToken]:
        """Добавить токен (идентификатор) устройства в бд"""
        device_for_user = await FirebaseDeviceTokenDao.find_by_filter(session, {"device_token": token})
        if device_for_user is None:
            return await FirebaseDeviceTokenDao.add_one(session, {"holder_id": user_id, "device_token": token})
        raise SuchDeviceTokenAlreadyExist
