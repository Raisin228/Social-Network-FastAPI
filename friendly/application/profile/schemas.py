import unicodedata

from pydantic import BaseModel, Field, model_validator


def check_single_alphabet(value: str) -> None | tuple[str, str]:
    """Все символы строки из одного алфавита"""
    first_char_script = get_script(value[0])
    for char in value:
        if get_script(char) != first_char_script:
            return None

    return value, first_char_script


def get_script(char: str) -> str:
    """Определить алфавит символа"""
    return unicodedata.name(char).split(" ")[0]


class AdditionalProfileInfo(BaseModel):
    """Параметры запроса при редактировании профиля"""

    first_name: str | None = Field(examples=["Marie"], default=None, max_length=32, min_length=2)
    last_name: str | None = Field(examples=["St. Jacques"], default=None, max_length=32, min_length=1)

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
    def is_valid_name_and_last_name(cls, values: dict):
        f_name: str | None = values.get("first_name")
        l_name: str | None = values.get("last_name")

        cls.__is_correct(f_name)
        cls.__is_correct(l_name)

        alphabet1 = check_single_alphabet(f_name)
        alphabet2 = check_single_alphabet(l_name)
        if alphabet1 is None or alphabet2 is None or alphabet1[1] != alphabet2[1]:
            raise ValueError("All fields must be filled in the same language")
        return values
