from uuid import UUID

from application.auth.dependensies import get_current_user_access_token
from application.auth.models import User
from application.core.exceptions import DataDoesNotExist, RequestToYourself
from application.core.responses import BAD_REQUEST, FORBIDDEN, NOT_FOUND, UNAUTHORIZED
from application.friends.dao import FriendDao
from application.friends.models import Relations
from application.friends.schemas import FriendRequestSent
from database import get_async_session
from fastapi import APIRouter, Depends, HTTPException, Query
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
            detail="Such a request has already been sent earlier. Duplicates not allowed",
        )
    except DataDoesNotExist:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    except RequestToYourself as ex:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=ex.msg)

    # TODO прислать уведомление 2му пользователю
    return FriendRequestSent(**{"sender": result.user_id, "recipient": result.friend_id})


@router.get("/friend/incoming_friend_requests")
async def view_entire_appeal(
    offset: int = Query(0, ge=0),
    limit: int = Query(10, gt=0, le=50),
    user: User = Depends(get_current_user_access_token),
    session: AsyncSession = Depends(get_async_session),
):
    """Получить список всех входящих запросов на дружбу"""

    res = await FriendDao.get_income_appeal(session, offset, limit, user.id)
    for i in res:
        print(i)
    # return res


@router.patch("/friend/accept/{friend_id}")
async def approve_friend_request(
    friend_id: UUID,
    user: User = Depends(get_current_user_access_token),
    session: AsyncSession = Depends(get_async_session),
):
    res = await FriendDao.update_row(
        session, {"relationship_type": Relations.FRIEND}, {"user_id": friend_id, "friend_id": user.id}
    )
    print(res)
