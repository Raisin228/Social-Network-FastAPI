import pytest
from application.profile.request_body import AdditionalProfileInfo


class TestAdditionalProfileInfo:
    """Проверяем валидаторы класса AdditionalProfileInfo"""

    incorrect_dates = [
        ("1853-05-24", "the date of birth must be after 1900"),
        ("3000-10-29", "you couldn't have been born in the future"),
    ]

    incorrect_initials = [
        ("B0gdan", "Atros!henko", "numbers and special characters are prohibited"),
        (
            "CamelCase",
            "bigLetterS",
            "all fields must be filled in with a capital letter besides you "
            "cannot use multiple capital letters in one word",
        ),
        ("Богдан", "Atroshenko", "all fields must be filled in the same language"),
    ]

    @pytest.mark.parametrize("date, msg", incorrect_dates)
    def test_update_profile_incorrect_date(self, date: str, msg: str):
        """Не валидная дата рождения пользователя"""
        with pytest.raises(ValueError, match=msg):
            AdditionalProfileInfo(**{"birthday": date})

    @pytest.mark.parametrize("name, second_name, msg", incorrect_initials)
    def test_incorrect_fl_name(self, name: str, second_name: str, msg: str):
        """Валидные ли имя и фамилия пользователя"""
        with pytest.raises(ValueError, match=msg):
            AdditionalProfileInfo(**{"first_name": name, "last_name": second_name})

    def test_incorrect_nickname(self):
        """Валидный ли nick"""
        with pytest.raises(
            ValueError, match="nickname can only consist of Latin letters, numbers, underscore and dash"
        ):
            AdditionalProfileInfo(**{"nickname": "ioqwrh!@32344*(фыав"})
