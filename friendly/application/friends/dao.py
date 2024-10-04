from typing import List
from uuid import UUID

from application.auth.dao import UserDao
from application.auth.models import User
from application.core.exceptions import DataDoesNotExist, RequestToYourself
from application.friends.models import Friend, Relations
from data_access_object.base import BaseDAO
from sqlalchemy import and_, case, insert, null, select
from sqlalchemy.ext.asyncio import AsyncSession


class FriendDao(BaseDAO):
    model = Friend

    @classmethod
    async def friend_request(cls, session: AsyncSession, values: dict) -> model:
        """Создать запрос на дружбу. Cтатус: (NOT_APPROVE)"""

        if values.get("user_id") == values.get("friend_id"):
            raise RequestToYourself
        if await UserDao.find_by_filter(session, {"id": values.get("friend_id")}) is None:
            raise DataDoesNotExist

        stmt = insert(cls.model).values(values)
        await session.execute(stmt)
        await session.commit()
        return cls.model(**values)

    @classmethod
    async def get_income_appeal(cls, session: AsyncSession, offset, limit, friend_id: UUID) -> List:
        """Получить входящие запросы на дружду"""
        query = (
            select(Friend.relationship_type, User.id, User.first_name, User.last_name, User.nickname, User.birthday)
            .join(User, User.id == Friend.user_id)
            .where(and_(Friend.relationship_type == Relations.NOT_APPROVE, Friend.friend_id == friend_id))
            .order_by(
                case(
                    (User.last_name.isnot(None), User.last_name),
                    (User.last_name.is_(None), null()),
                ),
                case((User.first_name.isnot(None), User.first_name), (User.first_name.is_(None), null())),
                User.id,
            )
            .offset(offset)
            .limit(limit)
        )

        print(query)
        data = await session.execute(query)
        return list(data.fetchall())
