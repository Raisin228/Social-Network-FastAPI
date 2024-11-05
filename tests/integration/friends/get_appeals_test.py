from application.core.responses import SUCCESS
from application.friends.dao import FriendDao
from application.friends.models import Relations
from httpx import AsyncClient
from integration.friends.conftest import get_two_users
from sqlalchemy.ext.asyncio import AsyncSession
from utils import get_token_need_type


async def test_other_user_friends(_create_standard_user, ac: AsyncClient, session: AsyncSession):
    """Тест. Получить список друзей другого пользователя"""
    store = await get_two_users(_create_standard_user, session)
    await FriendDao.friend_request(
        session, {"user_id": store[1].get("id"), "friend_id": store[0].get("id"), "relationship_type": Relations.FRIEND}
    )

    resp = await ac.get(
        f'/users/friends?whose_friends_usr_id={store[0].get("id")}',
        headers={"Authorization": f"Bearer {get_token_need_type(store[1].get('id'))}"},
    )
    assert resp.status_code == list(SUCCESS.keys())[0]
    assert resp.json() == [
        {
            "first_name": "Bog",
            "last_name": None,
            "birthday": None,
            "nickname": f'{store[1].get("nickname")}',
            "status": "FRIEND",
            "friend_id": f'{store[1].get("id")}',
        }
    ]


async def test_income_requests(_create_standard_user, ac: AsyncClient, session: AsyncSession):
    """Тест. Получить входящие запросы на дружбу"""
    store = await get_two_users(_create_standard_user, session)
    await FriendDao.friend_request(session, {"user_id": store[1].get("id"), "friend_id": store[0].get("id")})

    resp = await ac.get(
        "/users/friend/incoming_friend_requests",
        headers={"Authorization": f"Bearer {get_token_need_type(store[0].get('id'))}"},
    )
    assert resp.status_code == list(SUCCESS.keys())[0]
    assert resp.json() == [
        {
            "first_name": "Bog",
            "last_name": None,
            "birthday": None,
            "nickname": f'id_{store[1].get("id")}',
            "status": "NOT_APPROVE",
            "sender_id": f'{store[1].get("id")}',
        }
    ]
