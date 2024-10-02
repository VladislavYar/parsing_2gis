class ParserSettings:
    """Настройки парсера."""

    WEBSITE = 'https://2gis.ru'
    SLUG_CITY = 'moscow'
    SLUG_FIRM = 'firm'
    SLUG_RUBRICS = 'rubrics'
    SLUG_SUBRUBRICS = 'subrubrics'
    SLUG_RUBRIC_ID = 'rubricId'

    CLASS_RUBRICS = '_x4ac6o'
    CLASS_CONTENT_BLOCK = '_r47nf'
    CLASS_SUBRUBRICS = '_1rehek'
    CLASS_FIRM = '_1kf6gff'
    CLASS_FIRM_BLOCK = '_awwm2v'
    CLASS_NEXT_PAGE_FIRMS = '_n5hmn94'
    CLASS_ADDRESS_BLOCK = '_14quei'
    CLASS_ADDRESS = '_1w9o2igt'
    CLASS_NAME_BLOCK = '_zjunba'
    CLASS_NAME = '_1cd6avd'

    VALIDATE_NAME_CITY = 'Москва'
    LOG_LEVEL = 'log-level=3'


class GUISettings:
    """Настройки графического интерфейса."""

    MAX_ROW_CONSOLE = 21
    FORMAT_TIME = '%H:%M:%S'

    REGULAR_NAME_CITY = r'^[А-ЯЁ][а-яё]+(?:[ _-][А-ЯЁ][а-яё]+)*$'
    REGULAR_SLUG = r'^[a-z0-9]+(?:[_-][a-z0-9]+)*$'
    REGULAR_URL = (
        r'^(?:http|https)?://'
        r'(?:(?:[A-z0-9](?:[A-z0-9-]{0,61}[A-z0-9])?\.)'
        r'+(?:[A-z]{2,6}\.?|[A-z0-9-]{2,}\.?)|'
        r'localhost|'
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'
        r'(?::\d+)?'
        r'(?:/?|[/?]\S+)$'
    )
    REGULAR_PHONE = r'^\+7\d{10}$'
    REGULAR_EMAIL = (
        r'(?:[a-z0-9!#$%&'
        r"'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*|"
        r'"(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21\x23-\x5b\x5d-\x7f]|'
        r'\\[\x01-\x09\x0b\x0c\x0e-\x7f])*")@(?:(?:[a-z0-9]'
        r'(?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?|'
        r'\[(?:(?:25[0-5]|2[0-4][0-9]|'
        r'[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|'
        r'[01]?[0-9][0-9]?|[a-z0-9-]*[a-z0-9]:'
        r'(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21-\x5a\x53-\x7f]|'
        r'\\[\x01-\x09\x0b\x0c\x0e-\x7f])+)\])'
    )
    REGULAR_WORK_SCHEDULE = r'^\d{2}:\d{2}$'

    MAX_LEN_NAME = 255
    MAX_LEN_ADDRESS = 255
    MAX_LEN_IMAGE_HREF = 255
    MAX_LEN_EMAIL = 255
    MAX_LEN_SITE = 255

    KEY_DAY = ('Fri', 'Mon', 'Sat', 'Sun', 'Thu', 'Tue', 'Wed')
