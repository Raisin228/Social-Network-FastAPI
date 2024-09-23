import uuid
from typing import Literal

from application.auth.request_body import Email
from application.profile.request_body import AdditionalProfileInfo
from pydantic import BaseModel, ConfigDict, Field


class AccessTokenInfo(BaseModel):
    """Токен доступа"""

    access_token: str = Field(examples=["JWT_token.generated.friendly"], description="some_access_token")
    token_type: Literal["Bearer"] = Field(examples=["Bearer"])

    model_config = ConfigDict(extra="forbid")


class TokensInfo(AccessTokenInfo):
    """Токены доступа (access | refresh)"""

    refresh_token: str = Field(examples=["JWT_token.generated.friendly"], description="some_refresh_token")

    model_config = ConfigDict(extra="forbid")


class BasicUserFields(Email):
    """Основные поля пользовательского аккаунта"""

    id: uuid.UUID


class GetUser(BasicUserFields, AdditionalProfileInfo):
    """Все данные пользователя"""

    ...


class UserUpdatePassword(BasicUserFields):
    """После смены пароля"""

    msg: Literal["User's password successfully updated"] = Field(default="User's password successfully updated")


class UserRegister(BaseModel):
    """Аккаунт пользователя успешно создан"""

    msg: Literal["Account successfully created"]
    detail: GetUser

    model_config = ConfigDict(from_attributes=True, extra="forbid")


class ResetPasswordByEmail(Email):
    """Был выполнен запрос на получение ссылки для сброса пароля"""

    msg: Literal["The email has been sent successfully"] = Field(default="The email has been sent successfully")


class RedirectUserAuth(BaseModel):
    """Выполнен запрос на вход через учётную запись стороннего сервиса"""

    msg: str = Field(default="Redirects the user to OAuth server for authentication")
