from typing import List
from uuid import UUID

from application.auth.dependensies import get_current_user_access_token
from application.auth.models import User
from application.core.exceptions import (
    BlockByUser,
    DataDoesNotExist,
    NotApproveAppeal,
    RequestToYourself,
    UserUnblocked,
    YouNotFriends,
)
from application.core.responses import BAD_REQUEST, FORBIDDEN, NOT_FOUND, UNAUTHORIZED
from application.friends.dao import FriendDao
from application.friends.schemas import (
    ApplyFriend,
    DeleteFriendship,
    Friend,
    FriendRequestSent,
    IncomeRequests,
    UserBlockUnblock,
)
from database import get_async_session
from fastapi import APIRouter, Depends, HTTPException, Query
from firebase.notification import (
    NotificationEvent,
    get_notification_message,
    prepare_notification,
)
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

router = APIRouter(prefix="/users", tags=["Users"])


@router.post(
    "/friend/add/{friend_id}",
    response_model=FriendRequestSent,
    responses=BAD_REQUEST | FORBIDDEN | UNAUTHORIZED | NOT_FOUND,
)
async def send_friend_request(
    friend_id: UUID,
    user: User = Depends(get_current_user_access_token),
    session: AsyncSession = Depends(get_async_session),
):
    """Отправить запрос на дружбу"""
    try:
        result = await FriendDao.friend_request(session, {"user_id": user.id, "friend_id": friend_id})
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Such a request has already been sent earlier or you have been blocked. Duplicates not allowed",
        )
    except DataDoesNotExist:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    except RequestToYourself as ex:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=ex.msg)

    noty_msg = get_notification_message(NotificationEvent.FRIEND_REQUEST, user.nickname)
    await prepare_notification(user, friend_id, session, NotificationEvent.FRIEND_REQUEST, noty_msg)

    return FriendRequestSent(**{"sender": result.user_id, "recipient": result.friend_id})


@router.get("/my-friends", response_model=List[Friend], responses=FORBIDDEN | UNAUTHORIZED)
async def all_people_we_are_friends_with(
    offset: int = Query(0, ge=0),
    limit: int = Query(10, gt=0, le=50),
    user: User = Depends(get_current_user_access_token),
    session: AsyncSession = Depends(get_async_session),
):
    """Просмотреть список моих друзей"""
    friends = await FriendDao.get_all_friends(session, offset, limit, user.id)
    return [
        Friend(status=f[0], friend_id=f[1], first_name=f[2], last_name=f[3], nickname=f[4], birthday=f[5])
        for f in friends
    ]


@router.get("/friend/incoming_friend_requests", response_model=List[IncomeRequests], responses=FORBIDDEN | UNAUTHORIZED)
async def view_entire_appeal(
    offset: int = Query(0, ge=0),
    limit: int = Query(10, gt=0, le=50),
    user: User = Depends(get_current_user_access_token),
    session: AsyncSession = Depends(get_async_session),
):
    """Получить список всех входящих запросов на дружбу"""

    res = await FriendDao.get_income_appeal(session, offset, limit, user.id)
    return [
        IncomeRequests(
            status=row[0], sender_id=row[1], first_name=row[2], last_name=row[3], nickname=row[4], birthday=row[5]
        )
        for row in res
    ]


@router.patch(
    "/friend/accept/{friend_id}",
    response_model=ApplyFriend,
    responses=FORBIDDEN | UNAUTHORIZED | NOT_FOUND | BAD_REQUEST,
)
async def approve_friend_request(
    friend_id: UUID,
    user: User = Depends(get_current_user_access_token),
    session: AsyncSession = Depends(get_async_session),
):
    """Принять входящий запрос на дружбу"""
    try:
        res = await FriendDao.approve_friend_appeal(user, friend_id, session)
    except RequestToYourself:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="You can't make yourself a friend")
    except DataDoesNotExist:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="There is no active friendship application")
    except NotApproveAppeal as ex:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"{ex} You are either already friends or you have been blocked.",
        )

    notify_msg = get_notification_message(NotificationEvent.APPROVE_APPEAL, user.nickname)
    await prepare_notification(user, friend_id, session, NotificationEvent.APPROVE_APPEAL, notify_msg)

    data = res[0]
    return ApplyFriend(**{"friend_id": data[0]})


@router.put(
    "/ban_user/{ban_user_id}",
    response_model=UserBlockUnblock,
    responses=FORBIDDEN | UNAUTHORIZED | BAD_REQUEST | NOT_FOUND,
)
async def ban_annoying_user(
    ban_user_id: UUID,
    user: User = Depends(get_current_user_access_token),
    session: AsyncSession = Depends(get_async_session),
):
    """[Заблокировать | разблокировать] определённого пользователя

    **Note:**
    1) Пользователь не сможет отправлять ВАМ запросы на дружбу
    2) Будет удалён из списка друзей
    """
    try:
        await FriendDao.block_user(session, user.id, ban_user_id)

        notify_msg = get_notification_message(NotificationEvent.BAN, user.nickname)
        await prepare_notification(user, ban_user_id, session, NotificationEvent.BAN, notify_msg)

        return UserBlockUnblock(**{"msg": "This user has been added to blacklist", "block_user_id": ban_user_id})
    except BlockByUser as ex:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail=f"{ex.msg}. You can't block someone who blocked you"
        )
    except UserUnblocked:
        msg_info = get_notification_message(NotificationEvent.BLOCK_TERMINATE, user.nickname)
        await prepare_notification(user, ban_user_id, session, NotificationEvent.BLOCK_TERMINATE, msg_info)
        return UserBlockUnblock(
            **{"msg": "This user has been removed from the blacklist", "block_user_id": ban_user_id}
        )
    except RequestToYourself as ex:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=ex.msg)
    except DataDoesNotExist as ex:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"{ex.msg} The user with this ID was not found"
        )


@router.delete(
    "/friend/remove/{friend_id}", response_model=DeleteFriendship, responses=NOT_FOUND | UNAUTHORIZED | FORBIDDEN
)
async def end_friendship_with_user(
    friend_id: UUID,
    user: User = Depends(get_current_user_access_token),
    session: AsyncSession = Depends(get_async_session),
):
    """Удалить пользователя из списка друзей"""
    try:
        await FriendDao.end_friendship_with(user.id, friend_id, session)
    except YouNotFriends:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="You aren't friends with the user")

    notify_msg = get_notification_message(NotificationEvent.END_FRIENDSHIP, user.nickname)
    await prepare_notification(user, friend_id, session, NotificationEvent.END_FRIENDSHIP, notify_msg)
    return DeleteFriendship(**{"former_friend_id": friend_id})
