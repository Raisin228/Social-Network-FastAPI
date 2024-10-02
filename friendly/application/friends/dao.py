from application.auth.dao import UserDao
from application.core.exceptions import DataDoesNotExist
from application.friends.models import Friend
from data_access_object.base import BaseDAO
from sqlalchemy import insert
from sqlalchemy.ext.asyncio import AsyncSession


class FriendDao(BaseDAO):
    model = Friend

    @classmethod
    async def friend_request(cls, session: AsyncSession, values: dict) -> model:
        """Создать запрос на дружбу. Cтатус: (NOT_APPROVE)"""
        if await UserDao.find_by_filter(session, {"id": values.get("friend_id")}) is None:
            raise DataDoesNotExist

        stmt = insert(cls.model).values(values)
        await session.execute(stmt)
        await session.commit()
        return cls.model(**values)
