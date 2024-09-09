import pytest
from application.profile.utils import check_single_alphabet, get_script


class TestUtilsFunctions:
    input_data_get_script = [
        ("A", "LATIN"),
        ("Я", "CYRILLIC"),
        ("4", "DIGIT"),
        (",", "COMMA"),
        ("愛", "CJK"),
        ("incorrect_string_expect_one_char", "Some alphabet"),
    ]

    input_data_single_alphabet = [
        ("Hello world!", "LATIN"),
        ("   Эй Богдан. Я здесь!", "CYRILLIC"),
        ("   ", "Must be error"),
        ("Привет my name is Jason", "Must be ValueError"),
    ]

    @pytest.mark.parametrize("char, expected_result", input_data_get_script)
    def test_get_script(self, char: str, expected_result: str):
        """Правильно ли get_script определяет алфавит символа"""
        try:
            result = get_script(char)
            assert result == expected_result
        except TypeError as e:
            assert str(e) == "name() argument 1 must be a unicode character, not str"

    @pytest.mark.parametrize("data_string, expected_alphabet", input_data_single_alphabet)
    def test_check_single_alphabet(self, data_string: str, expected_alphabet: str):
        """Все символы в передаваемых строках должны быть одного алфавита"""
        try:
            result = check_single_alphabet(data_string)
            assert data_string == result[0]
            assert result[1] == expected_alphabet
        except ValueError as e:
            assert str(e) in [
                "all fields must be filled in the same language",
                "the string must contain at least one character other than a space",
            ]
