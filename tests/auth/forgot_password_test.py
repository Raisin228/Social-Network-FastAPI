from unittest.mock import AsyncMock

from application.auth.constants import RESET_PASSWORD_TOKEN_TYPE
from application.auth.dao import UserDao
from application.auth.request_body import NewPassword
from application.auth.schemas import ResetPasswordByEmail, UserUpdatePassword
from application.core.responses import NOT_FOUND, SUCCESS
from auth.hashing_password import verify_password
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from utils import USER_DATA, get_token_need_type


class TestForgotPassword:
    async def test_get_email_with_reset_link_user_does_not_exist(self, ac: AsyncClient, _mock_send_message: AsyncMock):
        """Запрос на сброс пароля [через почту] для пользователя, которого нет в системе"""
        response = await ac.post("/auth/single_link_to_password_reset", json={"email": USER_DATA["email"]})

        assert response.status_code == list(NOT_FOUND.keys())[0]
        assert response.json() == {"detail": "User with 'testuser@example.com' email address doesn't exist"}
        assert not _mock_send_message.called

    async def test_get_reset_password_link_to_email(
        self, _create_standard_user, ac: AsyncClient, _mock_send_message: AsyncMock
    ):
        """Отправить письмо для сброса пароля существующему в системе пользователю"""
        response = await ac.post("/auth/single_link_to_password_reset", json={"email": USER_DATA["email"]})

        assert response.status_code == list(SUCCESS.keys())[0]
        assert ResetPasswordByEmail.model_validate(response.json())
        assert _mock_send_message.called

    async def test_reset_password_by_link_from_email(
        self, _create_standard_user, ac: AsyncClient, session: AsyncSession
    ):
        """Пользователь меняет пароль, используя токен из письма"""
        data = NewPassword(**{"new_password": "uX8Tjtj_Xw", "confirm_new_password": "uX8Tjtj_Xw"})
        als = RESET_PASSWORD_TOKEN_TYPE
        response = await ac.patch(
            "/auth/replace_existent_password",
            json=dict(data),
            headers={"Authorization": f"Bearer {get_token_need_type(_create_standard_user.id, als)}"},
        )

        assert response.status_code == list(SUCCESS.keys())[0]
        assert UserUpdatePassword.model_validate(response.json())
        update_data = await UserDao.find_by_filter(session, {"email": _create_standard_user.email})
        assert verify_password("uX8Tjtj_Xw", update_data["password"])
