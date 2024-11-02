class BaseSettings:
    """Базовые настройки."""

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

    MAX_LEN_ADDRESS = 255
    MAX_LEN_EMAIL = 255
    MAX_LEN_SITE = 255


class ParserSettings(BaseSettings):
    """Настройки парсера."""

    WEBSITE = 'https://2gis.ru'
    SLUG_CITY = 'moscow'
    SLUG_RUBRICS = 'rubrics'
    SLUG_SUBRUBRICS = 'subrubrics'
    SLUG_RUBRIC_ID = 'rubricId'

    API_2GIS = 'https://catalog.api.2gis.ru'
    API_2GIS_ITEMS = '/3.0/items'
    API_HASH = 'baf4c54e9dae'
    API_FIELDS = (
        'items.adm_div,items.name_ex,items.external_content,'
        'items.contact_groups,items.address,items.schedule,'
        'items.org'
    )
    SIZE_PAGE = 50
    GX = 33
    MX = 5381

    CLASS_RUBRICS = '_x4ac6o'
    CLASS_CONTENT_BLOCK = '_r47nf'
    CLASS_SUBRUBRICS = '_1rehek'

    VALIDATE_NAME_CITY = 'Москва'
    MAX_PAGE = 834
    USER_AGENT = (
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) '
        'AppleWebKit/537.36 (KHTML, like Gecko) '
        'Chrome/50.0.2661.102 Safari/537.36'
    )
    ARGS_OPTION = (
        '--log-level=3',
        '--blink-settings=imagesEnabled=false',
        '--start-maximized',
        '--disable-infobars',
        '--disable-extensions',
        '--no-sandbox',
        '--disable-application-cache',
        '--disable-gpu',
        '--disable-dev-shm-usage',
        '-–nouse-idle-notification',
        '--ignore-certificate-errors',
    )
    BLOCKED_URLS = (
        'https://favorites.api.2gis.*/*',
        'https://2gis.*/_/log',
        'https://2gis.*/_/metrics',
        'https://tile0.maps.2gis.com/*',
        'https://disk.2gis.com/*',
        'https://ext.clickstream.sberbank.ru/*',
        'https://google-analytics.com/*',
        'https://www.google-analytics.com/*',
        'https://counter.yadro.ru/*',
        'https://www.tns-counter.ru/*',
        'https://mc.yandex.ru/*',
        'https://catalog.api.2gis.ru/3.0/ads/*',
        'https://d-assets.2gis.*/privacyPolicyBanner*.js',
        'https://vk.com/*',
        'https://d-assets.2gis.*/fonts/*',
        'https://mapgl.2gis.*/api/fonts/*',
        'https://tile*.maps.2gis.*',
        'https://s*.bss.2gis.*',
        'https://styles.api.2gis.*',
        'https://video-pr.api.2gis.*',
        'https://api.photo.2gis.*/*',
        'https://market-backend.api.2gis.*',
        'https://traffic*.edromaps.2gis.*',
        'https://disk.2gis.*/styles/*',
    )
    PARSING_BRANCHES = False
    KEYS_SKIP_SCHEDULE = (
        'comment',
        'is_24x7',
        'date_from',
        'date_to',
        'description',
    )


class GUISettings(BaseSettings):
    """Настройки графического интерфейса."""

    MAX_ROW_CONSOLE = 21
    FORMAT_TIME = '%H:%M:%S'

    REGULAR_NAME_CITY = r'^[А-ЯЁ][а-яё]+(?:[ _-][А-ЯЁ][а-яё]+)*$'
    REGULAR_SLUG = r'^[a-z0-9]+(?:[_-][a-z0-9]+)*$'
    REGULAR_WORK_SCHEDULE = r'^\d{2}:\d{2}$'
    REGULAR_ID_2GIS = r'^[1-9][0-9]*$'

    MAX_LEN_NAME = 255
    MAX_LEN_IMAGE_HREF = 255

    KEY_DAY = ('Fri', 'Mon', 'Sat', 'Sun', 'Thu', 'Tue', 'Wed')
