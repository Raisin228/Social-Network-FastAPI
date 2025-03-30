from unittest.mock import AsyncMock

from application.auth.dao import UserDao
from application.core.responses import CONFLICT, SUCCESS, UNPROCESSABLE_ENTITY
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from utils import USER_DATA


class TestRegistrationUser:
    async def test_uniq_user(
        self, ac: AsyncClient, session: AsyncSession, _mock_send_mail: AsyncMock
    ):
        """Регистрация аккаунта на почту, которая ещё не использовалась в системе"""
        response = await ac.post("/auth/registration", json=USER_DATA)

        assert response.status_code == list(SUCCESS.keys())[0]
        ans = response.json()
        ans["detail"].pop("id")
        ans["detail"].pop("nickname")
        assert ans == {
            "msg": "Account successfully created",
            "detail": {
                "email": USER_DATA.get("email"),
                "first_name": None,
                "last_name": None,
                "birthday": None,
                "sex": None,
                "is_admin": False,
            },
        }
        assert _mock_send_mail.called

        user_record = await UserDao.find_by_filter(session, {"email": USER_DATA["email"]})
        await UserDao.delete_by_filter(session, {"id": user_record["id"]})

    async def test_occupied_email(
        self, _create_standard_user, ac: AsyncClient, _mock_send_mail: AsyncMock
    ):
        """Регистрация пользователя на уже занятую почту"""
        response = await ac.post("/auth/registration", json=USER_DATA)
        assert response.status_code == list(CONFLICT.keys())[0]
        assert response.json() == {"detail": "User with that email already exist"}
        assert not _mock_send_mail.called

    async def test_invalid_input_data(
        self, ac: AsyncClient, session: AsyncSession, _mock_send_mail: AsyncMock
    ):
        """Не валидные данные для регистрации пользователя (неправильная почта и короткий пароль)"""
        incorrect_user_data = {"email": "incorrect_mail", "password": "123"}
        response = await ac.post("/auth/registration", json=incorrect_user_data)
        assert response.status_code == list(UNPROCESSABLE_ENTITY.keys())[0]
        assert not _mock_send_mail.called
        error_detail = response.json().get("detail", [])
        assert any(error["loc"] == ["body", "email"] for error in error_detail)
        assert any(error["loc"] == ["body", "password"] for error in error_detail)

        user_record = await UserDao.find_by_filter(session, {"email": "incorrect_mail"})
        assert user_record is None
