from fastapi import APIRouter, Depends, HTTPException, status

from application.auth.constants import ACCESS_TOKEN_TYPE, REFRESH_TOKEN_TYPE
from application.auth.dao import UserDao
from sqlalchemy.ext.asyncio import AsyncSession

from application.auth.dependensies import get_current_user_refresh_token, get_current_user_access_token
from application.auth.models import User
from application.core.responses import CONFLICT, UNAUTHORIZED, FORBIDDEN
from auth.auth import authenticate_user, create_jwt_token
from auth.hashing_password import hash_password
from database import get_async_session
from application.auth.schemas import UserRegister, GetUser, TokensInfo, AccessTokenInfo
from application.auth.request_body import UserRegistrationData

router = APIRouter(prefix='/auth', tags=['Auth'])


@router.post('/registration', summary='Register new user', response_model=UserRegister, responses=CONFLICT)
async def register_user(user_data: UserRegistrationData, session: AsyncSession = Depends(get_async_session)):
    """Регистрация пользователя по логину и паролю"""
    email = {'email': user_data.email}
    if await UserDao.find_by_filter(session, email):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='User with that email already exist')

    user_data = dict(user_data)
    user_data['password'] = hash_password(user_data['password'])
    result = await UserDao.add_one(session, user_data)

    response = UserRegister(
        msg="Account successfully created",
        detail=GetUser(**result.to_dict())
    )
    return response


@router.post('/login', summary='Log in to system', response_model=TokensInfo, responses=UNAUTHORIZED)
async def login_user(user_data: UserRegistrationData, session: AsyncSession = Depends(get_async_session)):
    """Вход в систему, получение JWT токена и запись его в cookies"""
    user = await authenticate_user(**user_data.model_dump(), session=session)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid email or password')

    data_for_payload = {'user_id': user['id']}
    access_token = create_jwt_token(data_for_payload, ACCESS_TOKEN_TYPE)
    refresh_token = create_jwt_token(data_for_payload, REFRESH_TOKEN_TYPE)
    return TokensInfo(access_token=access_token, refresh_token=refresh_token)


@router.post('/refresh_access_token', response_model=AccessTokenInfo, responses=UNAUTHORIZED | FORBIDDEN)
async def refresh_jwt(user: dict = Depends(get_current_user_refresh_token)):
    """Получить новый токен доступа"""
    data_for_payload = {'user_id': user['id']}
    access_token = create_jwt_token(data_for_payload, ACCESS_TOKEN_TYPE)
    return AccessTokenInfo(access_token=access_token)


@router.get('/secure')
def secure(user: User = Depends(get_current_user_access_token)):
    return user
