from typing import Dict

from application.auth.constants import (
    ACCESS_TOKEN_TYPE,
    REFRESH_TOKEN_TYPE,
    RESET_PASSWORD_TOKEN_TYPE,
    TOKEN_TYPE_FIELD,
)
from application.auth.dao import UserDao
from application.auth.schemas import GetUser
from auth.auth import decode_jwt
from database import get_async_session
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

security = HTTPBearer()


def checkup_token(req_token_type: str, identity) -> Dict | Exception:
    """Соответствует ли токен типу"""
    token = identity.credentials
    data = decode_jwt(token)
    type_from_jwt = data.get(TOKEN_TYPE_FIELD)
    if type_from_jwt is None or type_from_jwt != req_token_type:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Expected '{req_token_type}' get '{type_from_jwt}'",
        )
    return data


async def get_user_by_sub_id(token_payload: dict, session: AsyncSession) -> GetUser | None | Exception:
    """Достать пользователя из бд по user_id из payload"""
    user_id = token_payload.get("user_id")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Can't find a <user_id> in the jwt token",
        )

    data = await UserDao.find_by_filter(session, {"id": str(user_id)})
    if data is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return GetUser.model_validate(data)


def get_auth_user(token_type: str):
    """Получение пользователя на основе JWT"""

    async def get_user_from_token_type(
        credentials: HTTPAuthorizationCredentials = Depends(security),
        session: AsyncSession = Depends(get_async_session),
    ) -> Dict | None | Exception:
        payload = checkup_token(token_type, credentials)

        user = await get_user_by_sub_id(payload, session)
        return user

    return get_user_from_token_type


get_current_user_access_token = get_auth_user(ACCESS_TOKEN_TYPE)
get_current_user_refresh_token = get_auth_user(REFRESH_TOKEN_TYPE)
get_current_user_reset_password_token = get_auth_user(RESET_PASSWORD_TOKEN_TYPE)
