from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from application.auth.models import User
from data_access_object.base import BaseDAO


class UserDao(BaseDAO):
    model = User

    @classmethod
    async def find_one_or_none(cls, session: AsyncSession, find_by: dict) -> dict | None:
        """Получить одного пользователя по фильтрам"""
        query = select(cls.model).filter_by(**find_by)
        data = await session.execute(query)
        result = data.scalars().one_or_none()
        return cls.object_to_dict(result)

