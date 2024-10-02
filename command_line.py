from argparse import ArgumentParser, ArgumentTypeError
import re

from settings import GUISettings


def validate_slug_city(value: str) -> str:
    """Валидация slug города.

    Args:
        value (str): slug города.

    Raises:
        ArgumentTypeError: ошибка валидации.

    Returns:
        str: slug города.
    """
    reg = GUISettings.REGULAR_SLUG
    pattern = re.compile(reg)
    if not pattern.match(value):
        raise ArgumentTypeError(
            f'Slug города "{value}" не соответсвует '
            f'регулярному выражению: {reg}'
        )
    return value


def validate_name_city(value: str) -> str:
    """Валидация name города.

    Args:
        value (str): name города.

    Raises:
        ArgumentTypeError: ошибка валидации.

    Returns:
        str: name города.
    """
    reg = GUISettings.REGULAR_NAME_CITY
    pattern = re.compile(reg)
    if not pattern.match(value):
        raise ArgumentTypeError(
            f'Название города "{value}" не соответсвует '
            f'регулярному выражению: {reg}'
        )
    return value


def parser_command_line() -> ArgumentParser:
    """Парсер командной строки."""
    parser = ArgumentParser(description='Парсер фирм с 2GIS')
    parser.add_argument(
        '-g',
        '--gui',
        action='store_true',
        help='Вызов графического интерфейса',
    )
    parser.add_argument(
        '-n',
        '--name',
        help='Название города',
        type=validate_name_city,
        default='Москва',
        required=False,
    )
    parser.add_argument(
        '-s',
        '--slug',
        help='Slug города',
        type=validate_slug_city,
        default='moscow',
        required=False,
    )
    return parser
