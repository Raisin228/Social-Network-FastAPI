from datetime import datetime, timezone, timedelta

from jose import jwt
from config import settings

auth_data = settings.auth_data


def create_access_token(data: dict) -> str:
    """Создание JWT токена"""
    payload = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=30)
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

