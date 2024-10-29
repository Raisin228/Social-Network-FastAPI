import uuid

from application.auth.constants import ACCESS_TOKEN_TYPE, REFRESH_TOKEN_TYPE
from auth.auth import create_jwt_token
from auth.hashing_password import hash_password

USER_DATA = {
    "email": "testuser@example.com",
    "password": "very_strong_user_password123",
}

UNIQ_ID = uuid.uuid4()

id_second = uuid.uuid4()

rows = [
    {
        "id": UNIQ_ID,
        "first_name": "Bog",
        "last_name": None,
        "birthday": None,
        "sex": None,
        "nickname": f"id_{UNIQ_ID}",
        "email": USER_DATA["email"],
        "password": hash_password(USER_DATA["password"]),
    },
    {
        "id": id_second,
        "first_name": "Bog",
        "last_name": None,
        "birthday": None,
        "sex": None,
        "nickname": f"id_{id_second}",
        "email": "lambdadev@gmail.com",
        "password": hash_password(USER_DATA["password"]),
    },
]


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
