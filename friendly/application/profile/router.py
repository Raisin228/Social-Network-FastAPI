from application.auth.dao import UserDao
from application.auth.dependensies import get_current_user_access_token
from application.auth.models import User
from application.auth.schemas import GetUser
from application.core.responses import FORBIDDEN, UNAUTHORIZED
from application.profile.schemas import AdditionalProfileInfo
from database import get_async_session
from fastapi import APIRouter, Depends

router = APIRouter(prefix="/profile", tags=["User Profile"])


@router.get("/profile", response_model=GetUser, responses=FORBIDDEN | UNAUTHORIZED)
async def user_profile(user: User = Depends(get_current_user_access_token)):
    """Получить информацию о своём профиле"""
    return user


@router.patch("/profile", response_model=GetUser, responses=FORBIDDEN | UNAUTHORIZED)
async def change_profile(
    addition_info: AdditionalProfileInfo,
    user: User = Depends(get_current_user_access_token),
    session=Depends(get_async_session),
):
    """Изменить информацию в своём профиле"""
    data_aft_update = await UserDao.update_row(session, dict(addition_info), {"id": user.id})

    columns = [column.name for column in User.__table__.columns]
    if type(data_aft_update) == list:
        element = data_aft_update[0]
        return dict(zip(columns, element))
    return data_aft_update
