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

    REGULAR_NAME_CITY = r'^[А-ЯЁ][а-яё]+(?:[ _-][А-ЯЁ][а-яё]+)*$'
    REGULAR_SLUG_CITY = r'^[a-z0-9]+(?:[_-][a-z0-9]+)*$'
    MAX_ROW_CONSOLE = 21
    FORMAT_TIME = '%H:%M:%S'