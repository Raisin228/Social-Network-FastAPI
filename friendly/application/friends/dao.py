from typing import List, Tuple
from uuid import UUID

from application.auth.dao import UserDao
from application.auth.models import User
from application.core.exceptions import DataDoesNotExist
from application.friends.exceptions import (
    BlockByUser,
    NotApproveAppeal,
    RequestToYourself,
    UserUnblocked,
    YouNotFriends,
)
from application.friends.models import Friend, Relations
from data_access_object.base import BaseDAO
from sqlalchemy import BooleanClauseList, Select, and_, case, insert, null, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession


class FriendDao(BaseDAO):
    model = Friend

    @staticmethod
    def _bool_expression_constructor(friendship: str, user: UUID) -> BooleanClauseList:
        """Конструктор bool выражения для where"""
        conditions = [Friend.friend_id == user]

        if friendship == Relations.FRIEND:
            conditions.append(Friend.user_id == user)
        bool_expression = and_(Friend.relationship_type == friendship, or_(*conditions))
        return bool_expression

    @staticmethod
    def _constructor_select_friends(offset: int, limit: int, friendship_type: str, user: UUID) -> Select[User]:
        """Конструктор select запроса для выбора входящих запросов на дружбу и списка друзей"""
        condition = FriendDao._bool_expression_constructor(friendship_type, user)
        join_condition = Friend.user_id == User.id
        if friendship_type == Relations.FRIEND:
            join_condition = case(
                (Friend.user_id == user, User.id == Friend.friend_id), else_=User.id == Friend.user_id
            )  # pragma: no cover

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
        """Создать запрос на дружбу."""

        if values.get("user_id") == values.get("friend_id"):
            raise RequestToYourself()
        if await UserDao.find_by_filter(session, {"id": values.get("friend_id")}) is None:
            raise DataDoesNotExist

        stmt = insert(cls.model).values(values)
        await session.execute(stmt)
        await session.commit()
        return cls.model(**values)

    @classmethod
    async def get_all_friends(cls, session: AsyncSession, offset, limit, user: UUID) -> List[Tuple]:
        """Получить список всех пользователей, с которыми мы дружим"""
        query = FriendDao._constructor_select_friends(offset, limit, Relations.FRIEND.value, user)
        data = await session.execute(query)
        return [tuple(friend) for friend in data]

    @classmethod
    async def get_income_appeal(cls, session: AsyncSession, offset, limit, usr_id: UUID) -> List[Tuple]:
        """Получить входящие запросы на дружду"""
        query = FriendDao._constructor_select_friends(offset, limit, Relations.NOT_APPROVE.value, usr_id)
        data = await session.execute(query)
        return [tuple(row) for row in data]

    @classmethod
    async def approve_friend_appeal(cls, user: User, friend_id: UUID, session: AsyncSession) -> List[Tuple] | Exception:
        """Принять запрос на дружбу"""
        user_request_from_him = await FriendDao.find_by_filter(session, {"user_id": friend_id, "friend_id": user.id})
        usr_request_from_us = await FriendDao.find_by_filter(session, {"user_id": user.id, "friend_id": friend_id})

        if (
            user_request_from_him is not None and user_request_from_him["relationship_type"] != Relations.NOT_APPROVE
        ) or (usr_request_from_us is not None and usr_request_from_us["relationship_type"] != Relations.NOT_APPROVE):
            raise NotApproveAppeal()
        elif user_request_from_him is None and usr_request_from_us is None:
            raise DataDoesNotExist
        return await FriendDao.update_row(
            session, {"relationship_type": Relations.FRIEND}, {"user_id": friend_id, "friend_id": user.id}
        )

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
            raise YouNotFriends()

        search_pattern = {"user_id": is_friends.user_id, "friend_id": is_friends.friend_id}
        deleted_row = await FriendDao.delete_by_filter(session, search_pattern)
        return deleted_row

    @classmethod
    async def block_user(cls, session: AsyncSession, user_id: UUID, blocked_user_id: UUID) -> List[Tuple]:
        """Добавить пользователя в черный список"""

        user_order_1 = {"user_id": user_id, "friend_id": blocked_user_id}
        user_order_2 = {"user_id": blocked_user_id, "friend_id": user_id}

        if user_id == blocked_user_id:
            raise RequestToYourself()

        # нельзя заблокировать пользователя если он уже это сделал
        is_we_block = await FriendDao.find_by_filter(session, {**user_order_2, "relationship_type": Relations.BLOCKED})
        if is_we_block:
            raise BlockByUser()

        # при повторном запросе user будет разблокирован
        data = {**user_order_1, "relationship_type": Relations.BLOCKED}
        is_he_block_now = await FriendDao.find_by_filter(session, data)
        if is_he_block_now:
            await FriendDao.delete_by_filter(session, user_order_1)
            raise UserUnblocked()

        try:
            res = await FriendDao.friend_request(session, data)
        except IntegrityError:
            await session.rollback()
            res = await FriendDao.update_row(session, data, user_order_1)
            if not res:
                res = await FriendDao.update_row(session, data, user_order_2)
                if not res:
                    raise DataDoesNotExist
        return res
