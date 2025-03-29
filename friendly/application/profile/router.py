from typing import Dict

import sqlalchemy.exc
from application.auth.dependensies import get_current_user_access_token
from application.auth.models import User
from application.auth.schemas import GetUser
from application.core.exceptions import DataDoesNotExist
from application.core.responses import BAD_REQUEST, FORBIDDEN, NOT_FOUND, UNAUTHORIZED
from application.profile.dao import ProfileDao
from application.profile.request_body import AdditionalProfileInfo
from application.profile.schemas import AccountDeleted
from database import Transaction, get_async_session
from fastapi import APIRouter, Depends, HTTPException, Request
from redis_service import RedisService
from starlette import status

router = APIRouter(prefix="/profile", tags=["My Profile"])


# TODO внедри уже mypy для типизации


@router.get("/get_information", response_model=GetUser, responses=FORBIDDEN | UNAUTHORIZED)
@RedisService.cache_response(ttl=10)
async def user_profile(_request: Request, user: User = Depends(get_current_user_access_token)):
    """Получить информацию о своём профиле"""
    return user


@router.patch(
    "/update_information", response_model=GetUser, responses=FORBIDDEN | UNAUTHORIZED | NOT_FOUND | BAD_REQUEST
)
async def change_profile(
    addition_info: AdditionalProfileInfo,
    user: User = Depends(get_current_user_access_token),
    session=Depends(get_async_session),
) -> Dict:
    """Изменить информацию в своём профиле"""
    try:
        data_aft_update = await ProfileDao.update_row(session, dict(addition_info), {"id": str(user.id)})
        element = data_aft_update[0]
        columns = [column for column in User.get_column_names()]
        return dict(zip(columns, element))
    except DataDoesNotExist as ex:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=ex.msg)
    except sqlalchemy.exc.IntegrityError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="user with this nickname already exists")


@router.delete("/delete_account", response_model=AccountDeleted, responses=FORBIDDEN | UNAUTHORIZED)
async def delete_profile(user: User = Depends(get_current_user_access_token)):
    """Удалить свою учётную запись"""
    async with Transaction() as session:
        deleted_account = await ProfileDao.delete_by_filter(session, {"id": str(user.id)})
    deleted_account = deleted_account[0]

    columns = [column for column in User.get_column_names()]
    deleted_account = dict(zip(columns, deleted_account))
    return AccountDeleted(deleted_account_info=GetUser.model_validate(deleted_account))
