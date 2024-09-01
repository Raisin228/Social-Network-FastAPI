from datetime import datetime, timezone, timedelta

from fastapi import HTTPException, status
from jose import jwt, JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from application.auth.constants import REFRESH_TOKEN_TYPE, ACCESS_TOKEN_TYPE, TOKEN_TYPE_FIELD
from application.auth.dao import UserDao
from .hashing_password import verify_password
from config import settings

auth_data = settings.auth_data


def create_jwt_token(data: dict, token_type: str) -> str:
    """Создание токена"""
    payload = data.copy()

    if token_type == REFRESH_TOKEN_TYPE:
        exp_time = timedelta(days=30)
    elif token_type == ACCESS_TOKEN_TYPE:
        exp_time = timedelta(hours=1)
    else:
        raise ValueError('Incorrect jwt token type')
    expire = datetime.now(timezone.utc) + exp_time
    payload.update({
        TOKEN_TYPE_FIELD: token_type,
        'iss': 'friendly',
        'exp': expire,
        'iat': datetime.now(timezone.utc)
    })
    encode_jwt = jwt.encode(payload, auth_data['secret_key'], algorithm=auth_data['algorithm'])
    return encode_jwt


def decode_jwt(token: str) -> dict | Exception:
    """Декодирование JWT токена"""
    try:
        decoded_token = jwt.decode(token, auth_data['secret_key'], algorithms=auth_data['algorithm'])
        return decoded_token
    except JWTError as e:
        print(e)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Token invalid!')


async def authenticate_user(email: str, password: str, session: AsyncSession) -> dict | None:
    """Существует ли пользователь в системе"""
    user = await UserDao.find_by_filter(session, {'email': email})
    if user is None or not verify_password(password, user['password']):
        return None
    return user
