from pydantic import BaseModel, ConfigDict, Field


class AccessTokenInfo(BaseModel):
    access_token: str = Field(examples=['JWT_token.generated.friendly'], description='some_access_token')
    token_type: str = Field(examples=['Bearer'], default='Bearer')


class TokensInfo(AccessTokenInfo):
    """Токены доступа (access | refresh)"""
    refresh_token: str | None = Field(examples=['JWT_token.generated.friendly'], description='some_refresh_token',
                                      default=None)


class GetUser(BaseModel):
    """Данные пользователя"""
    id: int
    first_name: str | None
    last_name: str | None
    login: str


class UserRegister(BaseModel):
    """Аккаунт пользователя успешно создан"""
    model_config = ConfigDict(from_attributes=True)
    msg: str
    detail: GetUser
