from application.auth.constants import ACCESS_TOKEN_TYPE, REFRESH_TOKEN_TYPE
from application.auth.dao import UserDao
from application.core.responses import SUCCESS, UNAUTHORIZED, UNPROCESSABLE_ENTITY
from auth.auth import decode_jwt
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from utils import USER_DATA


class TestLogin:
    async def test_exist_user_with_correct_email_and_pass(self, _create_standard_user, ac: AsyncClient):
        """Пользователь существует в системе и пытается сделать вход"""
        response = await ac.post("/auth/login", json=USER_DATA)
        assert response.status_code == list(SUCCESS.keys())[0]
        data = response.json()
        access = decode_jwt(data.get("access_token"))
        refresh = decode_jwt(data.get("refresh_token"))
        assert access.get("token_type") == ACCESS_TOKEN_TYPE and access.get("user_id") == str(_create_standard_user.id)
        assert refresh.get("token_type") == REFRESH_TOKEN_TYPE and access.get("user_id") == str(
            _create_standard_user.id
        )

    async def test_non_existent_account(self, ac: AsyncClient, session: AsyncSession):
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

    async def test_user_invalid_input_data(self, ac: AsyncClient, session: AsyncSession):
        """Не валидные данные для входа (неправильная почта и короткий пароль)"""
        incorrect_user_data = {"email": "incorrect_mail", "password": "123"}
        response = await ac.post("/auth/login", json=incorrect_user_data)
        assert response.status_code == list(UNPROCESSABLE_ENTITY.keys())[0]
        error_detail = response.json().get("detail", [])
        assert any(error["loc"] == ["body", "email"] for error in error_detail)
        assert any(error["loc"] == ["body", "password"] for error in error_detail)

        user_record = await UserDao.find_by_filter(session, {"email": "incorrect_mail"})
        assert user_record is None
