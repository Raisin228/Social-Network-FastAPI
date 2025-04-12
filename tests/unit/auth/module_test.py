import pytest
from application.auth.request_body import NewPassword

param_data = [("password1", "password2"), ("raisin228", "geekon26")]


@pytest.mark.parametrize("pass1, pass2", param_data)
def test_new_pass_not_match_new_pass_confirm(pass1: str, pass2: str):
    """Не валидная дата рождения пользователя"""
    with pytest.raises(
        ValueError, match="the values in new_password and confirm_new_password must match"
    ):
        NewPassword(**{"new_password": pass1, "confirm_new_password": pass2})
