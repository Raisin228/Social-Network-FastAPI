from unittest.mock import AsyncMock, patch

import pytest
from utils import USER_DATA


@pytest.fixture()
def _mock_google_auth_request() -> AsyncMock:
    """Мок запроса на авторизацию через Google Auth"""
    with patch("auth.google_oauth.oauth.google.authorize_redirect", new_callable=AsyncMock) as mock_method:
        mock_method.return_value = {"msg": "Redirects the user to OAuth server for authentication"}
        yield mock_method


@pytest.fixture()
def _mock_google_auth_token() -> AsyncMock:
    """Выдача токена доступа и получение пользователя заменяем на шаблонный ответ"""
    with patch("application.auth.router.get_data_from_authorize_token", new_callable=AsyncMock) as mock_method:
        mock_method.return_value = {"email": USER_DATA["email"], "given_name": "Богдан", "family_name": "Атрошенко"}
        yield mock_method


@pytest.fixture()
def _mock_redirect_response() -> AsyncMock:
    """Имитация перенаправления из starlette"""
    with patch("application.auth.router.RedirectResponse") as mock:
        mock.return_value = {"detail": "Redirects the user to OAuth server for authentication"}
        yield mock


@pytest.fixture()
def _mock_ydex_access_token() -> AsyncMock:
    """Получение access токена от yandex"""
    with patch("application.auth.router.change_code_to_access_token") as mock:
        mock.return_value = "y0_AgAAAADgzq3NAAx7CAAAEAER6XzQAAAPiZ-6byJKopVvNOE2IsBaI_9KUw"
        yield mock


@pytest.fixture()
def _mock_ydex_change_token_to_user() -> AsyncMock:
    """Обменять ac_token ydex на данные пользователя"""
    with patch("application.auth.router.change_token_to_user_info") as mock:
        mock.return_value = {"first_name": "Богдан", "last_name": "Атрошенко", "default_email": USER_DATA["email"]}
        yield mock


@pytest.fixture()
def _mock_send_mail() -> AsyncMock:
    """Отправить письмо на почту через Celery"""
    with patch("application.auth.router.send_mail.delay") as mock:
        mock.return_value = {"message": "Email has been sent"}
        yield mock
