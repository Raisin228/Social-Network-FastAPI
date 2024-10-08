import datetime
from string import ascii_letters, digits
from typing import Dict, Literal

from application.profile.utils import check_single_alphabet
from pydantic import BaseModel, Field, field_validator, model_validator


class MinUserInformation(BaseModel):
    """Содержит основную информацию о пользователе"""

    first_name: str | None = Field(
        examples=["Jason"], description="User's name", default=None, max_length=32, min_length=2
    )
    last_name: str | None = Field(
        examples=["Jr. Borne"], description="User's surname", default=None, max_length=32, min_length=1
    )
    birthday: datetime.date | None = Field(examples=["2004-10-29"], description="User's birthday", default=None)
    nickname: str | None = Field(
        examples=["bog_at_04"],
        description="Short name to make it easier to find you or mention you in the entries",
        default=None,
        min_length=5,
    )


class AdditionalProfileInfo(MinUserInformation):
    """Параметры запроса при редактировании профиля"""

    sex: Literal["Man", "Woman"] | None = Field(examples=["Man"], description="User's gender", default=None)

    @field_validator("birthday")
    @classmethod
    def __is_correct_date(cls, date: datetime.date | None) -> Exception | datetime.date:
        """Соответствует ли дата рождения временному диапазону"""
        if date is not None:
            if date < datetime.date(1900, 1, 1):
                raise ValueError("the date of birth must be after 1900")
            elif date > datetime.date.today():
                raise ValueError("you couldn't have been born in the future")
        return date

    @staticmethod
    def __is_correct(data: str):
        if data is not None:
            if not any(map(lambda word: word.isalpha(), data.split())):
                raise ValueError(r"numbers and special characters are prohibited")
            elif data.title() != data:
                raise ValueError(
                    "all fields must be filled in with a capital letter besides you cannot use multiple capital "
                    "letters in one word"
                )

    @model_validator(mode="before")
    @classmethod
    def __is_valid_name_and_last_name(cls, values: dict) -> Dict:
        f_name: str | None = values.get("first_name")
        l_name: str | None = values.get("last_name")
        nick = values.get("nickname")

        cls.__is_correct(f_name)
        cls.__is_correct(l_name)

        alphabet1 = check_single_alphabet(f_name)
        alphabet2 = check_single_alphabet(l_name)
        if alphabet1 is not None and alphabet2 is not None and alphabet1[1] != alphabet2[1]:
            raise ValueError("all fields must be filled in the same language")

        if nick is not None and any(map(lambda char: char not in ascii_letters + digits + "_-", nick)):
            raise ValueError("nickname can only consist of Latin letters, numbers, underscore and dash")
        return values
