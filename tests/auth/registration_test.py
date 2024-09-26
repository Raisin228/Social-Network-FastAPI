from unittest.mock import AsyncMock
from uuid import UUID

from application.auth.dao import UserDao
from application.auth.schemas import UserRegister
from application.core.responses import CONFLICT, SUCCESS, UNPROCESSABLE_ENTITY
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from utils import USER_DATA


class TestRegistrationUser:
    async def test_uniq_user(self, ac: AsyncClient, session: AsyncSession, _mock_send_message: AsyncMock):
        """Регистрация аккаунта на почту, которая ещё не использовалась в системе"""
        response = await ac.post("/auth/registration", json=USER_DATA)

        assert response.status_code == list(SUCCESS.keys())[0]
        assert UserRegister.model_validate(response.json())
        assert _mock_send_message.called

        user_record = await UserDao.find_by_filter(session, {"email": USER_DATA["email"]})
        assert user_record["email"] == USER_DATA["email"]
        assert user_record["first_name"] is None
        assert user_record["last_name"] is None
        assert user_record["birthday"] is None
        assert user_record["sex"] is None
        assert user_record["nickname"] == f'id_{user_record["id"]}'
        await UserDao.delete_by_filter(session, {"id": user_record["id"]})

    async def test_occupied_email(
        self, _create_standard_user, ac: AsyncClient, session: AsyncSession, _mock_send_message: AsyncMock
    ):
        """Регистрация пользователя на уже занятую почту"""
        response = await ac.post("/auth/registration", json=USER_DATA)
        assert response.status_code == list(CONFLICT.keys())[0]
        assert response.json() == {"detail": "User with that email already exist"}
        assert not _mock_send_message.called

        user_record = await UserDao.find_by_filter(session, {"email": USER_DATA["email"]})
        assert isinstance(user_record["id"], UUID)
        assert user_record["email"] == USER_DATA["email"]
        assert user_record["first_name"] is None
        assert user_record["last_name"] is None

    async def test_invalid_input_data(self, ac: AsyncClient, session: AsyncSession, _mock_send_message: AsyncMock):
        """Не валидные данные для регистрации пользователя (неправильная почта и короткий пароль)"""
        incorrect_user_data = {"email": "incorrect_mail", "password": "123"}
        response = await ac.post("/auth/registration", json=incorrect_user_data)
        assert response.status_code == list(UNPROCESSABLE_ENTITY.keys())[0]
        assert not _mock_send_message.called
        error_detail = response.json().get("detail", [])
        assert any(error["loc"] == ["body", "email"] for error in error_detail)
        assert any(error["loc"] == ["body", "password"] for error in error_detail)

        user_record = await UserDao.find_by_filter(session, {"email": "incorrect_mail"})
        assert user_record is None
