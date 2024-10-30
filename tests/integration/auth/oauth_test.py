# from unittest import mock
# from unittest.mock import AsyncMock
#
# from application.auth.dao import UserDao
# from application.auth.models import User
# from application.auth.schemas import TokensInfo
# from application.core.responses import BAD_REQUEST, FOUND, SUCCESS
# from config import settings
# from httpx import AsyncClient
# from sqlalchemy.ext.asyncio import AsyncSession
# from utils import USER_DATA
#
#
# class TestGoogleOAuth:
#     """Регистрация/вход в приложение через Google"""
#
#     async def test_redirect_google_from_swagger(self, ac: AsyncClient):
#         """Перенаправить пользователя на Google Auth. Запрос через swagger"""
#         headers = {"referer": "/docs"}
#         response = await ac.get("/auth/login/via_google", headers=headers)
#
#         assert response.status_code == list(FOUND.keys())[0]
#         assert response.json() == {"msg": "Redirects the user to Google OAuth for authentication"}
#
#     async def test_redirect_google(self, ac: AsyncClient, _mock_google_auth_request: AsyncMock):
#         """Перенаправление через запрос с клиентского приложения"""
#         response = await ac.get("/auth/login/via_google")
#
#         _mock_google_auth_request.assert_called_once_with(
#             mock.ANY, "http://test/auth/callback/google", nonce=mock.ANY, prompt="consent"
#         )
#         assert response.status_code == list(FOUND.keys())[0]
#         assert response.json() == {"msg": "Redirects the user to OAuth server for authentication"}
#
#     async def test_callback_google_new_user(
#         self, session: AsyncSession, ac: AsyncClient, _mock_google_auth_token: AsyncMock
#     ):
#         """Новый пользователь регистрируется"""
#         response = await ac.get("/auth/callback/google")
#
#         _mock_google_auth_token.assert_called_once()
#         assert response.status_code == list(SUCCESS.keys())[0]
#         assert TokensInfo.model_validate(response.json())
#
#         await UserDao.delete_by_filter(session, {"email": USER_DATA["email"]})
#
#     async def test_callback_google_exist_user(
#         self, ac: AsyncClient, _mock_google_auth_token: AsyncMock, _create_standard_user: User
#     ):
#         """Сущ. пользователь входит в учётную запись"""
#         response = await ac.get("/auth/callback/google")
#
#         _mock_google_auth_token.assert_called_once()
#         assert response.status_code == list(SUCCESS.keys())[0]
#         assert TokensInfo.model_validate(response.json())
#
#     async def test_callback_google_failed(self, ac: AsyncClient):
#         """Пользователь прервал авторизацию через"""
#         response = await ac.get("/auth/callback/google")
#         assert response.status_code == list(BAD_REQUEST.keys())[0]
#         assert response.json() == {"detail": "Authorization failed or was canceled."}
#
#
# class TestYandexOAuth:
#     """Регистрация/вход в приложение через Yandex ID"""
#
#     async def test_redirect_yandex_from_swagger(self, ac: AsyncClient):
#         """Перенаправить пользователя на Yandex Auth. Запрос через swagger"""
#         headers = {"referer": "/docs"}
#         response = await ac.get("/auth/login/via_yandex", headers=headers)
#         assert response.status_code == list(FOUND.keys())[0]
#         assert response.json() == {"msg": "Redirects the user to Yandex OAuth for authentication"}
#
#     async def test_redirect_yandex(self, ac: AsyncClient, _mock_redirect_response: AsyncMock):
#         """Перенаправление через запрос с клиентского приложения"""
#         response = await ac.get("/auth/login/via_yandex")
#         _mock_redirect_response.assert_called_once_with(
#             f"https://oauth.yandex.ru/authorize?response_type=code&client_id={settings.YDEX_CLIENT_ID}&"
#             f"redirect_uri=http://test/auth/callback/yandex&force_confirm=true"
#         )
#         assert response.status_code == list(FOUND.keys())[0]
#         assert response.json() == {"msg": "Redirects the user to OAuth server for authentication"}
#
#     async def test_callback_yandex_lose_code(self, ac: AsyncClient):
#         """Нет кода подтверждения в пар.запроса"""
#         response = await ac.get("/auth/callback/yandex")
#         assert response.status_code == list(BAD_REQUEST.keys())[0]
#         assert response.json() == {"detail": "The confirmation code is missing."}
#
#     async def test_callback_yandex_failed(self, ac: AsyncClient, _mock_ydex_access_token: AsyncMock):
#         """Пользователь прервал авторизацию"""
#         response = await ac.get("/auth/callback/yandex", params={"code": 9999999})
#         assert response.status_code == list(BAD_REQUEST.keys())[0]
#         assert response.json() == {"detail": "Authorization failed or was canceled."}
#
#     async def test_callback_yandex_new_user(
#         self,
#         session: AsyncSession,
#         ac: AsyncClient,
#         _mock_ydex_access_token: AsyncMock,
#         _mock_ydex_change_token_to_user: AsyncMock,
#     ):
#         """Новый пользователь регистрируется через Yandex ID"""
#         response = await ac.get("/auth/callback/yandex", params={"code": 9999999})
#         _mock_ydex_access_token.assert_called_once()
#         _mock_ydex_change_token_to_user.assert_called_once()
#         assert response.status_code == list(SUCCESS.keys())[0]
#         assert TokensInfo.model_validate(response.json())
#
#         await UserDao.delete_by_filter(session, {"email": USER_DATA["email"]})
#
#     async def test_callback_yandex_exist_user(
#         self,
#         ac: AsyncClient,
#         _mock_ydex_access_token: AsyncMock,
#         _mock_ydex_change_token_to_user: AsyncMock,
#         _create_standard_user: User,
#     ):
#         """Сущ.пользователь входит в аккаунт через Yandex ID"""
#         response = await ac.get("/auth/callback/yandex", params={"code": 9999999})
#         _mock_ydex_access_token.assert_called_once()
#         _mock_ydex_change_token_to_user.assert_called_once()
#         assert response.status_code == list(SUCCESS.keys())[0]
#         assert TokensInfo.model_validate(response.json())
