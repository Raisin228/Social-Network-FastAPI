from pydantic import BaseModel, ConfigDict, Field


class GetAccessToken(BaseModel):
    """Токен доступа"""
    access_token: str = Field(..., examples=['JWT_token.generated.friendly'], description='some_jwt_token')


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
