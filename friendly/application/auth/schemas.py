from pydantic import BaseModel, ConfigDict


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
