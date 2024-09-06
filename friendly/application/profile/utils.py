import unicodedata


def check_single_alphabet(value: str | None) -> None | tuple[str, str]:
    """Все символы строки из одного алфавита"""
    if value is None:
        return None
    without_spaces = value.split()
    first_char_script = get_script(value[0])
    for word in without_spaces:
        if any(map(lambda char: char.isalpha() and get_script(char) != first_char_script, word)):
            raise ValueError("all fields must be filled in the same language")

    return value, first_char_script


def get_script(char: str) -> str:
    """Определить алфавит символа"""
    return unicodedata.name(char).split(" ")[0]
