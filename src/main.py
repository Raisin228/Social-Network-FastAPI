import uvicorn
from fastapi import FastAPI
from auth.base_config import auth_backend, fastapi_users
from auth.manager import get_user_manager
from auth.schemas import UserRead, UserCreate
from auth.utils import get_register_router
from posts.router import news_router
from profile.router import profile_router

# создание backend
app = FastAPI(
    title='Social Network',
    version='1.0'
)

# (роутер) login/logout
app.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix="/auth",
    tags=["Auth"],
)


# (роутер) регистрации
app.include_router(
    get_register_router(get_user_manager, UserRead, UserCreate),
    prefix="/auth",
    tags=["Auth"],
)


# (роутер) сброса пароля
app.include_router(
    fastapi_users.get_reset_password_router(),
    prefix="/auth",
    tags=["Auth"],
)

# (роутер) для взаимодействия с постами пользователей
app.include_router(news_router)

# (работа с профилем пользователя)
app.include_router(profile_router)


if __name__ == '__main__':
    uvicorn.run('main:app', port=8001)
