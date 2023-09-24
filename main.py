from fastapi import FastAPI, Depends
from fastapi_users import FastAPIUsers

from auth.auth import auth_backend
from auth.database import User
from auth.manager import get_user_manager
from auth.schemas import UserRead, UserCreate

# создание backend
app = FastAPI(
    title='Social Network',
    version='1.0'
)

fastapi_users = FastAPIUsers[User, int](
    get_user_manager,
    [auth_backend],
)

# (роутер) login/logout
app.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix="/auth",
    tags=["auth"],
)

# (роутер) регистрации
app.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["auth"],
)

current_user = fastapi_users.current_user()


@app.get("/profile", tags=["authorized_users"])
def get_authorized_greeting(user: User = Depends(current_user)):
    """Эндпоинт для отображения приветствия пользователям с jwt"""
    return f"Hello, {user.username}"


@app.get("/default_greeting", tags=["all_users"])
def unprotected_route():
    """Маршрут доступный всем пользователям"""
    return f"Hello, anonym"
