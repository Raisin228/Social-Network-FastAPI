import uuid
from typing import Literal

from application.profile.request_body import AdditionalProfileInfo
from pydantic import BaseModel, ConfigDict, EmailStr, Field


class AccessTokenInfo(BaseModel):
    """Токен доступа"""

    access_token: str = Field(examples=["JWT_token.generated.friendly"], description="some_access_token")
    token_type: Literal["Bearer"] = Field(examples=["Bearer"])

    model_config = ConfigDict(extra="forbid")


class TokensInfo(AccessTokenInfo):
    """Токены доступа (access | refresh)"""

    refresh_token: str = Field(examples=["JWT_token.generated.friendly"], description="some_refresh_token")

    model_config = ConfigDict(extra="forbid")


class GetUser(AdditionalProfileInfo):
    """Данные пользователя"""

    id: uuid.UUID
    email: EmailStr = Field(examples=["JasonBorne@gmail.com"], description="User's electronic mail")


class UserRegister(BaseModel):
    """Аккаунт пользователя успешно создан"""

    msg: Literal["Account successfully created"]
    detail: GetUser

    model_config = ConfigDict(from_attributes=True, extra="forbid")
