from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from application.auth.dao import UserDao
from sqlalchemy.ext.asyncio import AsyncSession

from application.core.responses import CONFLICT
from auth.hashing_password import hash_password
from database import get_async_session
from application.auth.schemas import UserRegister
from application.auth.request_body import UserRegistrationData

router = APIRouter(prefix='/auth', tags=['Auth'])


@router.post('/registration', summary='Register new user', response_model=UserRegister | None, responses=CONFLICT)
async def register_user(user_data: UserRegistrationData, session: AsyncSession = Depends(get_async_session)):
    """Регистрация пользователя по логину и паролю"""
    login = {'login': user_data.login}
    if await UserDao.find_one_or_none(session, login):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='User with that login already exist')

    user_data = dict(user_data)
    user_data['password'] = hash_password(user_data['password'])
    result = await UserDao.add_one(session, user_data)
    print(
        '==========================================================РЕЗУЛЬТАТ==========================================================',
        result)

    return result
