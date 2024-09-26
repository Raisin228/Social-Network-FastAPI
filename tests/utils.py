import uuid

from application.auth.constants import ACCESS_TOKEN_TYPE, REFRESH_TOKEN_TYPE
from auth.auth import create_jwt_token

USER_DATA = {
    "email": "testuser@example.com",
    "password": "very_strong_user_password123",
}

UNIQ_ID = uuid.uuid4()


def get_refresh_token(user_id: uuid.UUID = UNIQ_ID, is_incorrect: bool = False) -> str:
    """Получить refresh токен для конкретного user"""
    data = {"some_info": "lalala"} if is_incorrect else {"user_id": str(user_id)}
    return create_jwt_token(data, token_type=REFRESH_TOKEN_TYPE)


def get_token_need_type(user_id: uuid.UUID = UNIQ_ID, t_type: str = ACCESS_TOKEN_TYPE) -> str:
    """Получить токен нужного типа для конкретного user. Ф-ия для ручного вызова.
    По умолчанию выдаёт токен доступа
    """
    data = {"user_id": str(user_id)}
    return create_jwt_token(data, token_type=t_type)
