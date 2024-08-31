import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from application.auth.constants import REFRESH_TOKEN_TYPE
from application.auth.dao import UserDao
from auth.auth import create_jwt_token
from auth.hashing_password import hash_password

user_data = {
    'email': 'testuser@example.com',
    'password': 'very_strong_user_password123'
}


@pytest.fixture(scope='function')
async def _create_standard_user(session: AsyncSession):
    """Создание пользователя перед тестом и удаления после теста."""
    new_user = await UserDao.add_one(session,
                                     {'email': user_data['email'], 'password': hash_password(user_data['password'])})
    return new_user


# @pytest.fixture
# def get_refresh_token(user_id: int = 1) -> str:
#     """Получить refresh токен для конкретного user"""
#     data = {"user_id": user_id}
#     return create_jwt_token(data, token_type=REFRESH_TOKEN_TYPE)
