import uuid

from application.auth.models import User
from application.friends.dao import FriendDao
from application.friends.models import Friend, Relations
from sqlalchemy import and_, case, null, or_, select


def test_bool_expression_friend_relationship():
    """Пользователь может быть другом либо как инициатор либо как получатель. Важно чтоб запрос содержал тип 'дружба' и
    состояние пользователя (инициатор/получатель)"""
    user_id = uuid.uuid4()
    expression = FriendDao._bool_expression_constructor(Relations.FRIEND, user_id)

    assert expression.compare(
        and_(Friend.relationship_type == Relations.FRIEND, or_(Friend.friend_id == user_id, Friend.user_id == user_id))
    )


def test_bool_expression_not_approve():
    """В качестве входящего запроса пользователь ВСЕГДА только получатель"""
    user_id = uuid.uuid4()
    expression = FriendDao._bool_expression_constructor(Relations.NOT_APPROVE, user_id)

    assert expression.compare(and_(Friend.relationship_type == Relations.NOT_APPROVE, or_(Friend.friend_id == user_id)))


def test_constructor_select_not_approve_appeal():
    """Получить k входящих запросов на дружбу"""
    user_id = uuid.uuid4()
    expr = FriendDao._constructor_select_friends(0, 10, Relations.NOT_APPROVE, user_id)

    assert expr.compare(
        select(Friend.relationship_type, User.id, User.first_name, User.last_name, User.nickname, User.birthday)
        .join(User, Friend.user_id == User.id)
        .where(and_(Friend.relationship_type == Relations.NOT_APPROVE, or_(Friend.friend_id == user_id)))
        .order_by(
            case(
                (User.last_name.isnot(None), User.last_name),
                (User.last_name.is_(None), null()),
            ),
            case((User.first_name.isnot(None), User.first_name), (User.first_name.is_(None), null())),
            User.id,
        )
        .offset(0)
        .limit(10)
    )
