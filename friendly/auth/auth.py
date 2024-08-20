import asyncio
from datetime import datetime, timezone, timedelta

from jose import jwt

from application.auth.dao import UserDao
from friendly.auth.hashing_password import verify_password
from config import settings
from database import session_factory

auth_data = settings.auth_data


def create_access_token(data: dict) -> str:
    """Создание JWT токена"""
    payload = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=30)
    payload['iss'] = 'friendly'
    payload['exp'] = expire
    encode_jwt = jwt.encode(payload, auth_data['secret_key'], algorithm=auth_data['algorithm'])
    return encode_jwt


def decode_jwt(token: str) -> dict:
    """Декодирование JWT токена"""
    try:
        decoded_token = jwt.decode(token, auth_data['secret_key'], algorithms=auth_data['algorithm'])
        return decoded_token
    except Exception as e:
        print(e)
        return {}


async def authenticate_user(login: str, password: str) -> dict | None:
    """Существует ли пользователь в системе"""
    async with session_factory() as session:
        user = await UserDao.find_one_or_none(session, {'login': login})
    if user is None or not verify_password(password, user['password']):
        return None
    return user
