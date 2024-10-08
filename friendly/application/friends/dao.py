from typing import List, Tuple
from uuid import UUID

from application.auth.dao import UserDao
from application.auth.models import User
from application.core.exceptions import (
    DataDoesNotExist,
    RequestToYourself,
    YouNotFriends,
)
from application.friends.models import Friend, Relations
from data_access_object.base import BaseDAO
from sqlalchemy import BooleanClauseList, and_, case, insert, null, or_, select
from sqlalchemy.ext.asyncio import AsyncSession


class FriendDao(BaseDAO):
    model = Friend

    @staticmethod
    def __bool_expression_constructor(friendship: str, user: UUID) -> BooleanClauseList:
        """Конструктор bool выражения для where"""
        conditions = [Friend.friend_id == user]

        if friendship == Relations.FRIEND:
            conditions.append(Friend.user_id == user)
        bool_expression = and_(Friend.relationship_type == friendship, or_(*conditions))
        return bool_expression

    @staticmethod
    def __constructor_select_friends(offset: int, limit: int, friendship_type: str, user: UUID):
        """"""
        condition = FriendDao.__bool_expression_constructor(friendship_type, user)
        join_condition = Friend.user_id == User.id
        if friendship_type == Relations.FRIEND:
            join_condition = case(
                (Friend.user_id == user, User.id == Friend.friend_id), else_=User.id == Friend.user_id
            )

        return (
            select(Friend.relationship_type, User.id, User.first_name, User.last_name, User.nickname, User.birthday)
            .join(User, join_condition)
            .where(condition)
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
    async def get_all_friends(cls, session: AsyncSession, offset, limit, user: UUID) -> list[Tuple]:
        """Получить список всех пользователей, с которыми мы дружим"""
        query = FriendDao.__constructor_select_friends(offset, limit, Relations.FRIEND, user)
        data = await session.execute(query)
        return [tuple(friend) for friend in data]

    @classmethod
    async def get_income_appeal(cls, session: AsyncSession, offset, limit, friend_id: UUID) -> List[Tuple]:
        """Получить входящие запросы на дружду"""
        query = FriendDao.__constructor_select_friends(offset, limit, Relations.NOT_APPROVE, friend_id)
        data = await session.execute(query)
        return [tuple(row) for row in data]

    @classmethod
    async def end_friendship_with(cls, user: UUID, friend: UUID, session: AsyncSession) -> List[Tuple]:
        """Удалить друга"""
        expr_to_users = or_(
            and_(Friend.user_id == user, Friend.friend_id == friend),
            and_(Friend.user_id == friend, Friend.friend_id == user),
        )
        query = select(Friend).where(and_(expr_to_users, Friend.relationship_type == Relations.FRIEND))

        exec_qe = await session.execute(query)
        is_friends = exec_qe.scalar()
        if is_friends is None:
            raise YouNotFriends

        search_pattern = {"user_id": is_friends.user_id, "friend_id": is_friends.friend_id}
        deleted_row = await FriendDao.delete_by_filter(session, search_pattern)
        return deleted_row
