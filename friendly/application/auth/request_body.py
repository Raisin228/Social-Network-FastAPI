from pydantic import BaseModel, Field, ConfigDict, EmailStr


class UserRegistrationData(BaseModel):
    """Входные данные при регистрации"""
    model_config = ConfigDict(from_attributes=True)

    email: EmailStr = Field(min_length=6, max_length=100, examples=['your_email@gmail.com'])
    password: str = Field(min_length=6, max_length=100, examples=['your_password'])
