import pytest
from application.auth.dao import UserDao
from application.auth.request_body import ModifyPassword, NewPassword
from application.auth.schemas import UserUpdatePassword
from application.core.responses import BAD_REQUEST, SUCCESS
from auth.hashing_password import verify_password
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from utils import get_token_need_type


class TestChangePassword:
    param_data = [("password1", "password2"), ("raisin228", "geekon26")]

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
        assert UserUpdatePassword.model_validate(response.json())

        update_user = await UserDao.find_by_filter(session, {"email": _create_standard_user.email})
        assert verify_password("qwerty", update_user["password"])

    async def test_incorrect_cur_password(self, _create_standard_user, ac: AsyncClient, session: AsyncSession):
        """Пользователь указал неверный тек. пароль"""
        request_data = ModifyPassword(
            **{"current_password": "incorrect_password", "new_password": "qwerty", "confirm_new_password": "qwerty"}
        )
        response = await ac.post(
            "/auth/change_password",
            json=dict(request_data),
            headers={"Authorization": f"Bearer {get_token_need_type(_create_standard_user.id)}"},
        )

        assert response.status_code == list(BAD_REQUEST.keys())[0]
        assert response.json() == {
            "detail": "the password from the current_password field does not match your account password"
        }

        update_user = await UserDao.find_by_filter(session, {"email": _create_standard_user.email})
        assert verify_password("very_strong_user_password123", update_user["password"])

    @pytest.mark.parametrize("pass1, pass2", param_data)
    def test_new_pass_not_match_new_pass_confirm(self, pass1: str, pass2: str):
        """Не валидная дата рождения пользователя"""
        with pytest.raises(ValueError, match="the values in new_password and confirm_new_password must match"):
            NewPassword(**{"new_password": pass1, "confirm_new_password": pass2})
