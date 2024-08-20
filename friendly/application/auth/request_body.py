import re

from pydantic import BaseModel, Field, ConfigDict, field_validator


class UserRegistrationData(BaseModel):
    """Входные данные при регистрации"""
    model_config = ConfigDict(from_attributes=True)

    login: str = Field(min_length=6, max_length=100, examples=['your_login'])
    password: str = Field(min_length=6, max_length=100, examples=['your_password'])

    @field_validator('login')
    @classmethod
    def login_must_contain_only_latin_letters_numbers_underscores(cls, log: str) -> str:
        """Доп. валидация логина"""
        if re.search(r'[^a-zA-Z0-9_]', log) is not None or not any(map(lambda symbol: symbol.isalpha(), log)):
            raise ValueError(
                'The login can only consist of Latin letters, numbers and underscores! '
                'Must contain at least one letter.')
        return log
