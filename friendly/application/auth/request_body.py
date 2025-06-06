from typing import Dict

from pydantic import BaseModel, ConfigDict, EmailStr, Field, model_validator


class Email(BaseModel):
    email: EmailStr = Field(
        min_length=6,
        max_length=100,
        examples=["your_email@gmail.com"],
        description="User's electronic mail",
    )


class UserRegistrationData(Email):
    """Входные данные при регистрации"""

    model_config = ConfigDict(from_attributes=True)

    password: str = Field(min_length=6, max_length=100, examples=["your_password"])


class NewPassword(BaseModel):
    """Поля для ввода нового пароля"""

    new_password: str = Field(
        min_length=6, max_length=100, examples=["uX8Tjtj_Xw"], description="New password"
    )
    confirm_new_password: str = Field(
        min_length=6, max_length=100, examples=["uX8Tjtj_Xw"], description="Repeat password"
    )

    @model_validator(mode="before")
    @classmethod
    def __is_password_match(cls, values: dict) -> Dict:
        if values.get("new_password") != values.get("confirm_new_password"):
            raise ValueError("the values in new_password and confirm_new_password must match")
        return values


class ModifyPassword(NewPassword):
    """Схема запроса для смены текущего пароля"""

    model_config = ConfigDict(from_attributes=True)

    current_password: str = Field(
        min_length=6,
        max_length=100,
        examples=["your_password"],
        description="The password you want to change",
    )
