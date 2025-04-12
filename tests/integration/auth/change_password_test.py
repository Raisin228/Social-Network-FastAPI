from application.auth.request_body import ModifyPassword
from application.core.responses import BAD_REQUEST, SUCCESS
from auth.hashing_password import verify_password
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from utils import get_token_need_type


class TestChangePassword:
    async def test_new_password_with_correct_current(
        self, _create_standard_user, ac: AsyncClient, session: AsyncSession
    ):
        """Пользователь авторизован в системе, помнит текущий пароль и правильно вводит новый"""
        request_data = ModifyPassword(
            **{
                "current_password": "very_strong_user_password123",
                "new_password": "qwerty",
                "confirm_new_password": "qwerty",
            }
        )
        response = await ac.post(
            "/auth/change_password",
            json=dict(request_data),
            headers={"Authorization": f"Bearer {get_token_need_type(_create_standard_user.id)}"},
        )
        assert response.status_code == list(SUCCESS.keys())[0]
        assert response.json() == {
            "msg": "User's password successfully updated",
            "id": str(_create_standard_user.id),
            "email": _create_standard_user.email,
            "is_admin": False,
        }

        await session.refresh(_create_standard_user)
        assert verify_password("qwerty", _create_standard_user.password)

    async def test_incorrect_cur_password(self, _create_standard_user, ac: AsyncClient):
        """Пользователь указал неверный тек. пароль"""
        request_data = ModifyPassword(
            **{
                "current_password": "incorrect_password",
                "new_password": "qwerty",
                "confirm_new_password": "qwerty",
            }
        )
        response = await ac.post(
            "/auth/change_password",
            json=dict(request_data),
            headers={"Authorization": f"Bearer {get_token_need_type(_create_standard_user.id)}"},
        )

        assert response.status_code == list(BAD_REQUEST.keys())[0]
        assert response.json() == {
            "detail": "the password from the current_password field does not "
            "match your account password"
        }
        assert verify_password("very_strong_user_password123", _create_standard_user.password)
