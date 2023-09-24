from typing import Optional, Union

from fastapi import Depends, Request
from fastapi_users import BaseUserManager, IntegerIDMixin, InvalidPasswordException

from auth.database import User, get_user_db
from auth.schemas import UserCreate
from config import SECRET_USER_MANAGER

SECRET = SECRET_USER_MANAGER


class UserManager(IntegerIDMixin, BaseUserManager[User, int]):
    """Class for user management"""
    reset_password_token_secret = SECRET
    verification_token_secret = SECRET

    async def on_after_register(self, user: User, request: Optional[Request] = None):
        """Логирование (user.id) зарегистрировался в системе"""
        print(f"User {user.id} has registered.")

    async def validate_password(
            self,
            password: str,
            user: Union[UserCreate, User],
    ) -> None:
        """метод для валидации пароля при регистрации в системе"""
        if len(password) < 8:
            raise InvalidPasswordException(
                reason="Password should be at least 8 characters"
            )
        if user.email in password:
            raise InvalidPasswordException(
                reason="Password should not contain e-mail"
            )


async def get_user_manager(user_db=Depends(get_user_db)):
    yield UserManager(user_db)
