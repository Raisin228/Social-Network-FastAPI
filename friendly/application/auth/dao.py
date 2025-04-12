from typing import Dict

from application.auth.models import User
from auth.hashing_password import verify_password
from data_access_object.base import BaseDAO
from sqlalchemy.ext.asyncio import AsyncSession


class UserDao(BaseDAO):
    model = User

    @classmethod
    async def authenticate_user(
        cls, email: str, password: str, session: AsyncSession
    ) -> Dict | None:
        """Существует ли пользователь с таким логином? Совпадает ли пароль с хэшем в системе"""
        user = await UserDao.find_by_filter(session, {"email": email})
        if user is None or not verify_password(password, user["password"]):
            return None
        return user
