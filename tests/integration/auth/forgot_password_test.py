from unittest.mock import AsyncMock

from application.auth.constants import RESET_PASSWORD_TOKEN_TYPE
from application.auth.request_body import NewPassword
from application.core.responses import NOT_FOUND, SUCCESS
from auth.hashing_password import verify_password
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from utils import USER_DATA, get_token_need_type


class TestForgotPassword:
    async def test_get_email_with_reset_link_user_does_not_exist(self, ac: AsyncClient, _mock_send_mail: AsyncMock):
        """Запрос на сброс пароля [через почту] для пользователя, которого нет в системе"""
        response = await ac.post("/auth/single_link_to_password_reset", json={"email": USER_DATA["email"]})

        assert response.status_code == list(NOT_FOUND.keys())[0]
        assert response.json() == {"detail": "User with 'testuser@example.com' email address doesn't exist"}
        assert not _mock_send_mail.called

    async def test_get_reset_password_link_to_email(
        self, _create_standard_user, ac: AsyncClient, _mock_send_mail: AsyncMock
    ):
        """Отправить письмо для сброса пароля существующему в системе пользователю"""
        response = await ac.post("/auth/single_link_to_password_reset", json={"email": USER_DATA["email"]})

        assert response.status_code == list(SUCCESS.keys())[0]
        assert response.json() == {"email": _create_standard_user.email, "msg": "The email has been sent successfully"}
        _mock_send_mail.assert_called_once()

    async def test_reset_password_by_link_from_email(
        self, _create_standard_user, ac: AsyncClient, session: AsyncSession
    ):
        """Пользователь меняет пароль, используя токен из письма"""
        data = NewPassword(**{"new_password": "uX8Tjtj_Xw", "confirm_new_password": "uX8Tjtj_Xw"})
        alias = RESET_PASSWORD_TOKEN_TYPE
        response = await ac.patch(
            "/auth/replace_existent_password",
            json=dict(data),
            headers={"Authorization": f"Bearer {get_token_need_type(_create_standard_user.id, alias)}"},
        )

        assert response.status_code == list(SUCCESS.keys())[0]
        assert response.json() == {
            "id": str(_create_standard_user.id),
            "email": _create_standard_user.email,
            "msg": "User's password successfully updated",
        }
        await session.refresh(_create_standard_user)
        assert verify_password("uX8Tjtj_Xw", _create_standard_user.password)
