from application.auth.dao import UserDao
from application.auth.schemas import TokensInfo
from application.core.responses import SUCCESS, UNAUTHORIZED, UNPROCESSABLE_ENTITY
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from utils import USER_DATA


async def test_login_exist_user_with_correct_email_and_pass(
    _create_standard_user, ac: AsyncClient, session: AsyncSession
):
    """Пользователь существует в системе и пытается сделать вход"""
    response = await ac.post("/auth/login", json=USER_DATA)
    assert response.status_code == list(SUCCESS.keys())[0]
    assert TokensInfo.model_validate(response.json())

    user = await UserDao.find_by_filter(session, {"email": USER_DATA["email"]})
    assert user["first_name"] is None
    assert user["last_name"] is None
    assert user["birthday"] is None
    assert user["sex"] is None
    assert user["nickname"] == f'id_{user["id"]}'


async def test_login_by_non_existent_account(ac: AsyncClient, session: AsyncSession):
    """Вход в несуществующий аккаунт"""
    incorrect_data = {
        "email": "imagine_mail@yandex.ru",
        "password": "strong_but_useless_pass",
    }
    response = await ac.post("/auth/login", json=incorrect_data)
    assert response.status_code == list(UNAUTHORIZED.keys())[0]
    assert response.json() == {"detail": "Invalid email or password"}

    user_record = await UserDao.find_by_filter(session, {"email": incorrect_data["email"]})
    assert user_record is None


async def test_login_user_invalid_input_data(ac: AsyncClient, session: AsyncSession):
    """Не валидные данные для входа (неправильная почта и короткий пароль)"""
    incorrect_user_data = {"email": "incorrect_mail", "password": "123"}
    response = await ac.post("/auth/login", json=incorrect_user_data)
    assert response.status_code == list(UNPROCESSABLE_ENTITY.keys())[0]
    error_detail = response.json().get("detail", [])
    assert any(error["loc"] == ["body", "email"] for error in error_detail)
    assert any(error["loc"] == ["body", "password"] for error in error_detail)

    user_record = await UserDao.find_by_filter(session, {"email": "incorrect_mail"})
    assert user_record is None
