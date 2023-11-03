from fastapi_users import FastAPIUsers
from fastapi_users.authentication import CookieTransport, AuthenticationBackend
from fastapi_users.authentication import JWTStrategy

from auth.manager import get_user_manager
from auth.models import user
from config import MY_JWT_SECRET

JWT_SECRET = MY_JWT_SECRET


# выбираем транспортную стратегию
cookie_transport = CookieTransport(cookie_name='Auth-Social-Network', cookie_max_age=3600)


def get_jwt_strategy() -> JWTStrategy:
    """Configuration for jwt strategy"""
    return JWTStrategy(secret=JWT_SECRET, lifetime_seconds=3600 * 24, algorithm='HS256')


# создаём auth backend (объект который объединяет транспорт и стратегию)
auth_backend = AuthenticationBackend(
    name="jwt",
    transport=cookie_transport,
    get_strategy=get_jwt_strategy,
)

fastapi_users = FastAPIUsers[user, int](
    get_user_manager,
    [auth_backend],
)
