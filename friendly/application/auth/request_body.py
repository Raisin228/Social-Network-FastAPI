from pydantic import BaseModel, Field, ConfigDict


class UserRegistrationData(BaseModel):
    """Входные данные при регистрации"""
    model_config = ConfigDict(from_attributes=True)

    login: str = Field(min_length=6, max_length=100)
    password: str = Field(min_length=6, max_length=100)

