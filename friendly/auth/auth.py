from datetime import datetime, timedelta, timezone
from typing import Dict

from application.auth.constants import (
    ACCESS_TOKEN_TYPE,
    ADMIN_PANEL_ACCESS_TOKEN_TYPE,
    REFRESH_TOKEN_TYPE,
    RESET_PASSWORD_TOKEN_TYPE,
    TOKEN_TYPE_FIELD,
)
from config import settings
from fastapi import HTTPException, status
from jose import JWTError, jwt
from logger_config import log

auth_data = settings.auth_data


def create_jwt_token(data: dict, token_type: str) -> str:
    """Создание токена"""
    payload = data.copy()
    temp = {
        REFRESH_TOKEN_TYPE: timedelta(days=30),
        ACCESS_TOKEN_TYPE: timedelta(
            days=30, hours=24
        ),  # todo не забудь у acces изменить время жизни
        RESET_PASSWORD_TOKEN_TYPE: timedelta(hours=1),
        ADMIN_PANEL_ACCESS_TOKEN_TYPE: timedelta(minutes=1),
    }

    exp_time = temp.get(token_type)
    if exp_time is None:
        raise ValueError("Incorrect jwt token type")
    expire = datetime.now(timezone.utc) + exp_time
    payload.update(
        {
            TOKEN_TYPE_FIELD: token_type,
            "iss": "friendly",
            "exp": expire,
            "iat": datetime.now(timezone.utc),
        }
    )
    encode_jwt = jwt.encode(payload, auth_data["secret_key"], algorithm=auth_data["algorithm"])
    return encode_jwt


def decode_jwt(token: str) -> Dict | Exception:
    """Декодирование JWT токена"""
    try:
        decoded_token = jwt.decode(
            token, auth_data["secret_key"], algorithms=auth_data["algorithm"]
        )
        return decoded_token
    except JWTError as e:
        log.error(e)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token invalid!")
