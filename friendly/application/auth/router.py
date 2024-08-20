from fastapi import APIRouter, Depends, HTTPException, status
from fastapi import Response

from application.auth.dao import UserDao
from sqlalchemy.ext.asyncio import AsyncSession

from application.core.responses import CONFLICT, UNAUTHORIZED
from auth.auth import authenticate_user, create_access_token
from auth.hashing_password import hash_password
from database import get_async_session
from application.auth.schemas import UserRegister, GetUser, GetAccessToken
from application.auth.request_body import UserRegistrationData

router = APIRouter(prefix='/auth', tags=['Auth'])


@router.post('/registration', summary='Register new user', response_model=UserRegister, responses=CONFLICT)
async def register_user(user_data: UserRegistrationData, session: AsyncSession = Depends(get_async_session)):
    """Регистрация пользователя по логину и паролю"""
    login = {'login': user_data.login}
    if await UserDao.find_one_or_none(session, login):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='User with that login already exist')

    user_data = dict(user_data)
    user_data['password'] = hash_password(user_data['password'])
    result = await UserDao.add_one(session, user_data)

    response = UserRegister(
        msg="Account successfully created",
        detail=GetUser(**result.to_dict())
    )
    return response


@router.post('/login', summary='Log in to system', response_model=GetAccessToken, responses=UNAUTHORIZED)
async def login_user(user_data: UserRegistrationData, response: Response):
    """Вход в систему, получение JWT токена и запись его в cookies"""
    user = await authenticate_user(**user_data.dict())
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid login or password')

    data_for_payload = {'id': user['id']}
    access_token = create_access_token(data_for_payload)
    response.set_cookie(key='auth-tokens', value=access_token, max_age=31_536_000, httponly=True)
    return {'access_token': access_token}
