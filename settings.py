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


class ParserSettings(BaseSettings):
    """Настройки парсера."""

    WEBSITE = 'https://2gis.ru'
    SLUG_CITY = 'moscow'
    SLUG_FIRM = 'firm'
    SLUG_RUBRICS = 'rubrics'
    SLUG_SUBRUBRICS = 'subrubrics'
    SLUG_RUBRIC_ID = 'rubricId'
    API_2GIS = 'https://catalog.api.2gis.ru'
    API_2GIS_ITEMS = '/3.0/items'
    API_2GIS_BY_ID = f'{API_2GIS_ITEMS}/byid'
    API_HASH_BY_ID = 'baf4c54e9dae'
    API_FIELDS = (
        'items.locale,items.flags,search_attributes,items.adm_div,'
        'items.city_alias,items.region_id,items.segment_id,'
        'items.reviews,items.point,request_type,'
        'context_rubrics,query_context,items.links,items.name_ex,'
        'items.name_back,items.org,items.group,items.dates,'
        'items.external_content,items.contact_groups,items.comment,'
        'items.ads.options,items.email_for_sending.allowed,items.stat,'
        'items.stop_factors,items.description,items.geometry.centroid,'
        'items.geometry.selection,items.geometry.style,'
        'items.timezone_offset,items.context,items.level_count,'
        'items.address,items.is_paid,items.access,items.access_comment,'
        'items.for_trucks,items.is_incentive,items.paving_type,'
        'items.capacity,items.schedule,items.floors,ad,items.rubrics,'
        'items.routes,items.platforms,items.directions,items.barrier,'
        'items.reply_rate,items.purpose,items.purpose_code,'
        'items.attribute_groups,items.route_logo,items.has_goods,'
        'items.has_apartments_info,items.has_pinned_goods,'
        'items.has_realty,items.has_exchange,items.has_payments,'
        'items.has_dynamic_congestion,items.is_promoted,'
        'items.congestion,items.delivery,items.order_with_cart,'
        'search_type,items.has_discount,items.metarubrics,'
        'items.detailed_subtype,'
        'items.temporary_unavailable_atm_services,'
        'items.poi_category,items.structure_info.material,'
        'items.structure_info.floor_type,'
        'items.structure_info.gas_type,'
        'items.structure_info.year_of_construction,'
        'items.structure_info.elevators_count,'
        'items.structure_info.is_in_emergency_state,'
        'items.structure_info.project_type'
    )
    GX = 33
    MX = 5381

    CLASS_RUBRICS = '_x4ac6o'
    CLASS_CONTENT_BLOCK = '_r47nf'
    CLASS_SUBRUBRICS = '_1rehek'
    CLASS_FIRM_BLOCK = '_awwm2v'
    CLASS_NEXT_PAGE_FIRMS = '_n5hmn94'
    CLASS_PAGE = '_19xy60y'
    SELECTOR_PAGE = 'a._12164l30'
    SELECTOR_ACTIVE_PAGE = 'div._l934xo5 span._19xy60y'
    SELECTOR_LAST_PAGE = f'{SELECTOR_PAGE}:last-child'

    VALIDATE_NAME_CITY = 'Москва'
    MAX_RAM_GB = 3
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


class GUISettings(BaseSettings):
    """Настройки графического интерфейса."""

    MAX_ROW_CONSOLE = 21
    FORMAT_TIME = '%H:%M:%S'

    REGULAR_NAME_CITY = r'^[А-ЯЁ][а-яё]+(?:[ _-][А-ЯЁ][а-яё]+)*$'
    REGULAR_SLUG = r'^[a-z0-9]+(?:[_-][a-z0-9]+)*$'
    REGULAR_WORK_SCHEDULE = r'^\d{2}:\d{2}$'

    MAX_LEN_NAME = 255
    MAX_LEN_ADDRESS = 255
    MAX_LEN_IMAGE_HREF = 255
    MAX_LEN_EMAIL = 255
    MAX_LEN_SITE = 255

    KEY_DAY = ('Fri', 'Mon', 'Sat', 'Sun', 'Thu', 'Tue', 'Wed')
