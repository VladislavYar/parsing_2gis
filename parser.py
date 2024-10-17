from urllib.parse import urljoin, urlparse, parse_qs
from typing import Any
import json
import re

import requests
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver import Chrome, ChromeOptions
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import (
    NoSuchElementException,
    TimeoutException,
    WebDriverException,
)

from settings import ParserSettings
from exceptions import NoCityOn2GISException
from typings import RubricsData


class Parser(ParserSettings):
    """Парсер фирм в 2gis."""

    def __init__(self) -> None:
        """Инициализация драйвера парсера."""
        self.options = ChromeOptions()
        for arg_option in self.ARGS_OPTION:
            self.options.add_argument(arg_option)
        self.options.add_experimental_option('detach', True)
        self.options.set_capability(
            'goog:loggingPrefs', {'performance': 'ALL'}
        )
        self.service = Service(executable_path=ChromeDriverManager().install())
        self._start_driver()

    def _start_driver(self) -> None:
        """Запуск драйвера."""
        self.driver = Chrome(options=self.options, service=self.service)
        self.driver.execute_cdp_cmd(
            'Network.setBlockedURLs', {'urls': self.BLOCKED_URLS}
        )
        self.driver.execute_cdp_cmd('Network.enable', {})

    def _waiting_element(
        self,
        time: int | float,
        selector: str,
        by=By.CSS_SELECTOR,
    ) -> None:
        """Ожидание элемента.

        Args:
            time (int): время ожидания.
            selector (str): селектор элемента.
            by (str): способ поиска элемента.
        """
        WebDriverWait(self.driver, time).until(
            expected_conditions.presence_of_element_located(
                (
                    by,
                    selector,
                )
            )
        )

    def _get_rubrics(self) -> list[tuple[str, str, str]]:
        """Отдаёт список данных по рубрикам.

        Returns:
            list[tuple[str, str]]: список данных по рубрикам.
        """
        self.driver.get(
            urljoin(
                f'{urljoin(self.WEBSITE, self.SLUG_CITY)}/',
                self.SLUG_RUBRICS,
            )
        )
        if self.SLUG_CITY not in self.driver.current_url:
            raise NoCityOn2GISException(
                f'Город "{self.SLUG_CITY}" отсутсвует.',
            )
        a_rubrics = self.driver.find_elements(
            By.CSS_SELECTOR, f'a.{self.CLASS_RUBRICS}'
        )
        return [
            (
                a_rubric.get_attribute('title'),
                a_rubric.get_attribute('href'),
            )
            for a_rubric in a_rubrics
            if f'/{self.SLUG_SUBRUBRICS}/' in a_rubric.get_attribute('href')
        ]

    def _get_subrubrics(
        self,
        a_rubric: tuple[str, str],
        is_subrubric_subrubric: bool = False,
    ) -> list[tuple[str, str]]:
        """Отдаёт список данных по подрубрикам.

        Args:
            a_rubric (tuple[str, str]): данные по рубрике/подрубрике.
            is_subrubric_subrubric (bool): флаг подрубрики подрубрики.

        Returns:
            list[tuple[str, str]]: список данных по подрубрикам.
        """
        self.driver.get(a_rubric[1])
        if not is_subrubric_subrubric:
            selector = (
                f'.{self.CLASS_CONTENT_BLOCK}:nth-child(2) '
                f'a.{self.CLASS_RUBRICS}'
            )
            self._waiting_element(5, selector)
            a_subrubrics = self.driver.find_elements(By.CSS_SELECTOR, selector)
        else:
            selector = (
                f'.{self.CLASS_CONTENT_BLOCK}:nth-child(2) '
                f'a.{self.CLASS_SUBRUBRICS}'
            )
            try:
                self._waiting_element(5, selector)
                a_subrubrics = self.driver.find_elements(
                    By.CSS_SELECTOR,
                    selector,
                )
            except TimeoutException:
                a_subrubrics = []
        data_subrubrics = []
        a_subrubrics_subrubric = []
        for a_subrubric in a_subrubrics:
            if f'/{self.SLUG_RUBRIC_ID}/' in a_subrubric.get_attribute('href'):
                title = a_subrubric.get_attribute('title')
                if not title:
                    title = a_subrubric.get_attribute('textContent')
                data_subrubrics.append(
                    (
                        title.strip(),
                        a_subrubric.get_attribute('href'),
                    )
                )
            elif f'/{self.SLUG_SUBRUBRICS}/' in a_subrubric.get_attribute(
                'href'
            ):
                a_subrubrics_subrubric.append(
                    (
                        a_subrubric.get_attribute('title'),
                        a_subrubric.get_attribute('href'),
                        a_subrubric.get_attribute('href').split('/')[-1],
                    )
                )
        for a_subrubric_subrubric in a_subrubrics_subrubric:
            data_subrubrics.extend(
                self._get_subrubrics(a_subrubric_subrubric, True)
            )
        return data_subrubrics

    def _validate_address(self, firm: dict[str, Any]) -> bool:
        """Вадилация адреса.

        Args:
            firm (dict[str, str]): данные по фирме.

        Returns:
            bool: флаг валидации.
        """
        for location in firm['adm_div']:
            if location['type'] != 'city':
                continue
            if location['name'] == self.VALIDATE_NAME_CITY:
                return True
            return False
        return True

    def _get_image(self, firm_data: dict[str, Any]) -> str:
        """Отдаёт ссылку на изображение.

        Args:
            firm_data (dict[str, Any]): данные по фирме.

        Returns:
            str: ссылка на изображение.
        """
        external_content = firm_data.get('external_content')
        if not external_content:
            return ''
        for photo in external_content:
            if photo['subtype'] == 'common':
                return photo['main_photo_url']
        return ''

    def _get_address(self, firm_data: dict[str, Any]) -> str:
        """Отдаёт адрес фирмы.

        Args:
            firm_data (dict[str, Any]): данные по фирме.

        Returns:
            str: адрес фирмы.
        """
        address = firm_data.get('address_name')
        if not address:
            return self.VALIDATE_NAME_CITY
        return address

    def _get_contact(
        self,
        firm_data: dict[str, Any],
        key: str,
    ) -> str:
        """Отдаёт контакт фирмы по ключу.

        Args:
            firm_data (dict[str, Any]): данные по фирме.
            key (str): ключ контакта.

        Returns:
            str: контакт фирмы.
        """
        contact_groups = firm_data.get('contact_groups')
        if not contact_groups:
            return ''
        for contact_group in contact_groups:
            contacts = contact_group.get('contacts')
            if not contacts:
                continue
            for contact in contacts:
                if contact['type'] != key:
                    continue
                match key:
                    case 'phone':
                        value = contact['value']
                        if value[0] == '8':
                            value = f'+7{value[1:]}'
                        if re.compile(self.REGULAR_PHONE).match(value):
                            return value
                        return ''
                    case 'email':
                        value = contact['value']
                        if re.compile(self.REGULAR_EMAIL).match(value):
                            return value
                        return ''
                    case 'website':
                        value = contact['url']
                        if re.compile(self.REGULAR_URL).match(value):
                            return value
                        return ''
        return ''

    def _get_work_schedule(
        self,
        firm_data: dict[str, Any],
    ) -> dict[str, dict[str, str]]:
        """Отдаёт расписание фирмы.

        Args:
            firm_data (dict[str, Any]): данные по фирме.

        Returns:
            dict[str, dict[str, str]]: расписание фирмы.
        """
        schedule: dict[str, list[dict[str, str]]] = firm_data.get(
            'schedule', {}
        )
        if not schedule:
            schedule
        return {
            day: data['working_hours'][0]
            for day, data in schedule.items()
            if day not in ('comment', 'is_24x7')
        }

    def _get_name(self, firm: dict[str, Any]) -> str:
        """Отдаёт название организации.

        Args:
            firm (dict[str, Any]): данные по фирме.

        Returns:
            str: название огранизации.
        """
        if name := firm.get('name_ex', {}).get('primary'):
            return name
        return firm['name']

    def _get_request_id(self, check_string: str) -> str:
        """Отдаёт id запроса данных по фирме.

        Args:
            check_string (str): проверочная строка URL.

        Returns:
            str: данные по запросу.
        """
        entries = self.driver.get_log('performance')
        for entry in entries:
            message = json.loads(entry['message'])['message']
            if message['method'] != 'Network.requestWillBeSent':
                continue
            params = message['params']
            request_url = params['request']['url']
            if check_string not in request_url:
                continue
            return {
                'id': params['requestId'],
                'query': parse_qs(urlparse(request_url).query),
            }

    def signal_parse_firm(self, *arg, **kwarg) -> None:
        """Сигнал парсинга фирмы."""
        pass

    def _get_page_subrubric(self, url: str) -> None:
        """Переходит на страницу подрубрики.

        Args:
            url (str): URL подрубрики.
        """
        self.driver.get(url)

    def _get_last_page_subrubric(self, count_page: int) -> None:
        """Отдаёт последнюю страницу парсинга.

        Args:
            count_page (int): количество спаршенных страниц.
        """
        last_button_page = self.driver.find_element(
            By.CSS_SELECTOR, self.SELECTOR_LAST_PAGE
        )
        last_page = int(last_button_page.get_attribute('textContent'))
        if last_page < count_page or last_page == count_page:
            click_button_page = last_button_page
        else:
            click_button_page = self.driver.find_element(
                By.XPATH,
                f"//a/span[text()='{count_page}' "
                f"and @class='{self.CLASS_PAGE}']",
            )
        new_page = click_button_page.get_attribute('textContent')
        click_button_page.location_once_scrolled_into_view
        click_button_page.click()
        self._waiting_element(
            5,
            f"//div/span[text()='{new_page}' "
            f"and @class='{self.CLASS_PAGE}']",
            By.XPATH,
        )

    def _check_page(self, count_page: int) -> None:
        """Проверяет нахождение на спаршенной странице.

        Args:
            count_page (int): количество спаршенных страниц.
        """
        while True:
            current_page = int(
                self.driver.find_element(
                    By.CSS_SELECTOR, self.SELECTOR_ACTIVE_PAGE
                ).get_attribute('textContent')
            )
            if current_page == count_page:
                break
            self._get_last_page_subrubric(count_page)

    def _check_memory(self) -> bool:
        """Проверяет заполненность памяти браузером.

        Returns:
            bool: флаг перезапуска драйвера.
        """
        memory = (
            self.driver.execute_script('return window.performance.memory')[
                'usedJSHeapSize'
            ]
            / 1024
            / 1024
            / 1024
        )
        if memory >= self.MAX_RAM_GB:
            self.driver.close()
            self.driver.quit()
            self._start_driver()
            return False
        return True

    def _get_next_page_subrubric(self, count_page: int) -> None:
        """Переходит на новую страницу.

        Args:
            count_page (int): количество спаршенных страниц.
        """
        self._check_page(count_page)
        selector = f'div.{self.CLASS_NEXT_PAGE_FIRMS}:last-child'
        next_page = self.driver.find_element(By.CSS_SELECTOR, selector)
        next_page.location_once_scrolled_into_view
        next_page.click()
        self._waiting_element(5, f'div.{self.CLASS_FIRM_BLOCK}')

    def _get_data_response(self, request_id: str) -> dict[str, Any]:
        """Отдаёт словарь данных по запросу.

        Args:
            request_id (str): id запроса.

        Returns:
            dict[str, Any]: словарь данных по запросу.
        """
        while True:
            try:
                return json.loads(
                    self.driver.execute_cdp_cmd(
                        'Network.getResponseBody',
                        {'requestId': request_id},
                    )['body']
                )['result']
            except WebDriverException:
                continue

    def _get_firms_page(self, count_page: int) -> list[dict[str, Any]]:
        """Отдаёт фирмы на странице.

        Args:
            count_page (int): кол-во спаршенных страниц.

        Returns:
            list[dict[str, Any]]: список фирм.
        """
        if count_page > 0:
            data = self._get_data_response(
                self._get_request_id(self.API_2GIS_ITEMS)['id']
            )
            return data['items']
        else:
            return [
                firm['data']
                for firm in self.driver.execute_script(
                    'return initialState.data.entity.profile;'
                ).values()
            ]

    def _get_meta_data(self) -> dict[str, str | list[dict[str, float]]]:
        """Отдаёт meta данные 2GIS.

        Returns:
            tuple[str, str]: meta данные.
        """
        customcfg = self.driver.execute_script('return __customcfg;')
        tab_catalog = self.driver.execute_script(
            'return initialState.appContext.frames[0].tabCatalog;'
        )
        return {
            'user_id': customcfg['userId'],
            'stat_sid': customcfg['sessionId'],
            'key': customcfg['webApiKey'],
            'shv': customcfg['commitIsoDate'].split(':')[0].replace('T', '-'),
            'rubric_id': tab_catalog['rubricId'],
            'viewpoint': tab_catalog['viewpoint'],
        }

    def _get_params_r(self, data: dict[str, str]) -> str:
        """Отдаёт параметр r для запроса.

        Args:
            data (dict[str, str]): данные для вычисления.

        Returns:
            str: параметр r.
        """
        data_string = ''.join(data.values())
        return self.driver.execute_script(f"""
            const dataString = '{data_string}';
            const dataStringLength = dataString.length;
            let r = {self.MX};
            for (let i = 0; i < dataStringLength; i += 1)
                r = r * {self.GX} + dataString.charCodeAt(i),
                r >>>= 0;
            return r;
        """)

    def _get_url_firm(
        self,
        firm: dict[str, Any],
        meta_data: dict[str, str],
    ) -> str:
        """Отдаёт URL фирмы.

        Args:
            firm (dict[str, Any]): данные по фирме.
            meta_data (dict[str, str]): meta-данные.

        Returns:
            str: URL фирмы.
        """
        viewpoint = meta_data['viewpoint']
        viewpoint1 = f'{viewpoint[0]['lon']},{viewpoint[0]['lat']}'
        viewpoint2 = f'{viewpoint[1]['lon']},{viewpoint[1]['lat']}'
        data = {
            'api': self.API_2GIS_BY_ID,
            'context_rubrics[0]': meta_data['rubric_id'],
            'fields': self.API_FIELDS,
            'id': firm['id'],
            'key': meta_data['key'],
            'locale': firm['locale'],
            'search_ctx': f'0:r={meta_data['rubric_id']}',
            'shv': meta_data['shv'],
            'stat[sid]': meta_data['stat_sid'],
            'stat[user]': meta_data['user_id'],
            'viewpoint1': viewpoint1,
            'viewpoint2': viewpoint2,
            'hash': self.API_HASH_BY_ID,
        }
        data['r'] = self._get_params_r(data)
        return (
            f'{self.API_2GIS}{self.API_2GIS_BY_ID}?id={data['id']}&'
            f'key={data['key']}&locale={data['locale']}&'
            f'fields={data['fields']}&search_ctx={data['search_ctx']}&'
            f'context_rubrics[0]={data['context_rubrics[0]']}&'
            f'viewpoint1={data['viewpoint1']}&'
            f'viewpoint2={data['viewpoint2']}&stat[sid]={data['stat[sid]']}&'
            f'stat[user]={data['stat[user]']}&shv={data['shv']}&'
            f'r={data['r']}'
        )

    def _get_firm_from_api(self, url: str) -> dict[str, str]:
        """Отдаёт данные по фирме из API 2GIS.

        Args:
            url (str): URL запроса фирмы.

        Returns:
            dict[str, str]: данные по фирме из API 2GIS.
        """
        headers = {'User-Agent': self.USER_AGENT}
        response = requests.get(url, headers=headers)
        firm = response.json()['result']['items'][0]
        if not self._validate_address(firm):
            return {}
        return {
            'name': self._get_name(firm),
            'phone': self._get_contact(firm, 'phone'),
            'address': self._get_address(firm),
            'email': self._get_contact(firm, 'email'),
            'image_href': self._get_image(firm),
            'site': self._get_contact(firm, 'website'),
            'work_schedule': self._get_work_schedule(firm),
        }

    def _get_firms_data(
        self,
        firms: list[dict[str, Any]],
        meta_data: dict[str, str],
    ) -> list[dict[str, str]]:
        """Получает данные по фирмам из API.

        firms (list[dict[str, Any]]): спискок данных по фирмам.
        meta_data (dict[str, str]): мета данные для поиска.

        Returns:
            list[dict[str, str]]: список данных по фирмам.
        """
        data = []
        for firm in firms:
            url = self._get_url_firm(firm, meta_data)
            firm = self._get_firm_from_api(url)
            if not firm:
                continue
            data.append(firm)
            self.signal_parse_firm(firm)
        return data

    def _get_firms(self, a_subrubric: tuple[str, str]) -> list[dict[str, str]]:
        """Отдаёт список данных по фирмам.

        Args:
            a_subrubric (tuple[str, str]):  данные по подрубрике.

        Returns:
            list[dict[str, str]]: список данных по фирмам.
        """
        self._get_page_subrubric(a_subrubric[1])
        meta_data = self._get_meta_data()
        count_page = 0
        firms = []
        while True:
            firms_page = self._get_firms_page(count_page)
            firms.extend(self._get_firms_data(firms_page, meta_data))
            count_page += 1
            if not self._check_memory():
                self._get_page_subrubric(a_subrubric[1])
            try:
                self._get_next_page_subrubric(count_page)
            except NoSuchElementException:
                return firms

    def parsing(self) -> RubricsData:
        """Полный парсинг фирм с рубриками и подрубриками.

        Returns:
            RubricsData: данных по фирмам.
        """
        a_rubrics = self._get_rubrics()
        data = {}
        for a_rubric in a_rubrics:
            rubric_name = a_rubric[0]
            data[rubric_name] = {}
            a_subrubrics = self._get_subrubrics(a_rubric)
            for a_subrubric in a_subrubrics:
                firms = self._get_firms(a_subrubric)
                data[rubric_name][a_subrubric[0]] = firms
        return data
