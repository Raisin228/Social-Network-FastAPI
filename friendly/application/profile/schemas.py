from pydantic import BaseModel, Field, model_validator


class AdditionalProfileInfo(BaseModel):
    """Параметры запроса при редактировании профиля"""

    first_name: str | None = Field(examples=["Marie"], default=None, max_length=32, min_length=2)
    last_name: str | None = Field(examples=["St. Jacques"], default=None, max_length=32, min_length=1)

    @staticmethod
    def __is_correct(data: str):
        if data is not None:
            if any(map(lambda ch: ch.isdigit(), data)) or any(map(lambda ch: ch in r"/\|(!#$_%'()*)", data)):
                raise ValueError(r"numbers and special characters are prohibited /|(!#$_%'()*\)")
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
        return values
