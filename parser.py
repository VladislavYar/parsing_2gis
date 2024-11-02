from urllib.parse import urljoin
from typing import Any
import re
import asyncio

import aiohttp
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver import Chrome, ChromeOptions
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException

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
        for location in firm.get('adm_div', []):
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
        if not address or len(address) > self.MAX_LEN_ADDRESS:
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
                        if (
                            re.compile(self.REGULAR_EMAIL).match(value)
                            and len(value) <= self.MAX_LEN_EMAIL
                        ):
                            return value
                        return ''
                    case 'website':
                        value = contact['url']
                        if (
                            re.compile(self.REGULAR_URL).match(value)
                            and len(value) <= self.MAX_LEN_SITE
                        ):
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
            return schedule
        return {
            day: data['working_hours'][0]
            for day, data in schedule.items()
            if day not in self.KEYS_SKIP_SCHEDULE
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
        if name := firm.get('name'):
            return name
        return firm['full_name']

    def signal_parse_firms(self, *arg, **kwarg) -> None:
        """Сигнал парсинга фирм."""
        pass

    def _get_page_subrubric(self, url: str) -> None:
        """Переходит на страницу подрубрики.

        Args:
            url (str): URL подрубрики.
        """
        self.driver.get(url)

    def _get_meta_data(self) -> dict[str, str | list[dict[str, float]]]:
        """Отдаёт meta данные 2GIS.

        Returns:
            tuple[str, str]: meta данные.
        """
        customcfg = self.driver.execute_script('return __customcfg;')
        tab_catalog = self.driver.execute_script(
            'return initialState.appContext.frames[0].tabCatalog;'
        )
        rubric_data = self.driver.execute_script(
            """
            let profile = initialState.data.search.profile;
            return profile[Object.keys(profile)[0]].data;
            """
        )
        total = rubric_data['total']
        count_page = total // self.SIZE_PAGE
        if total % self.SIZE_PAGE:
            count_page += 1
        if total > self.MAX_PAGE:
            total = self.MAX_PAGE
        viewpoint = tab_catalog['viewpoint']
        viewpoint1 = f'{viewpoint[0]['lon']},{viewpoint[0]['lat']}'
        viewpoint2 = f'{viewpoint[1]['lon']},{viewpoint[1]['lat']}'
        return {
            'key': customcfg['webApiKey'],
            'viewpoint1': viewpoint1,
            'viewpoint2': viewpoint2,
            'rubric_id': rubric_data['rubrId'],
            'count_page': count_page,
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

    def _get_url_branches(
        self,
        firm: dict[str, Any],
        meta_data: dict[str, str],
        page: int,
    ) -> str:
        """Отдаёт URL филиалов.

        Args:
            firm (dict[str, Any]): данные по фирме.
            meta_data (dict[str, str]): meta-данные.
            page (int): страница филиалов.

        Returns:
            str: URL фирмы.
        """
        data = {
            'api': self.API_2GIS_ITEMS,
            'key': meta_data['key'],
            'org_id': firm['org']['id'],
            'page': f'{page}',
            'page_size': f'{self.SIZE_PAGE}',
            'search_disable_clipping_by_relevance': 'true',
            'type': 'branch',
            'viewpoint1': meta_data['viewpoint1'],
            'viewpoint2': meta_data['viewpoint2'],
            'hash': self.API_HASH,
        }
        data['r'] = self._get_params_r(data)
        return (
            f'{self.API_2GIS}{data['api']}?page={page}&'
            f'page_size={data['page_size']}&org_id={data['org_id']}&'
            f'key={data['key']}&type=branch&'
            f'search_disable_clipping_by_relevance=true&'
            f'viewpoint1={meta_data['viewpoint1']}&'
            f'viewpoint2={meta_data['viewpoint2']}&r={data['r']}'
        )

    def _get_url_firms_page(self, meta_data: dict[str, str], page: int) -> str:
        """Отдаёт URL страницы фирм.

        Args:
            meta_data (dict[str, str]): meta-данные.
            page (int) страница фирм.

        Returns:
            str: URL фирмы.
        """
        data = {
            'api': self.API_2GIS_ITEMS,
            'fields': self.API_FIELDS,
            'key': meta_data['key'],
            'page': f'{page}',
            'page_size': f'{self.SIZE_PAGE}',
            'rubric_id': meta_data['rubric_id'],
            'viewpoint1': meta_data['viewpoint1'],
            'viewpoint2': meta_data['viewpoint2'],
            'hash': self.API_HASH,
        }
        data['r'] = self._get_params_r(data)
        return (
            f'{self.API_2GIS}{data['api']}?page={page}&'
            f'page_size={data['page_size']}&rubric_id={data['rubric_id']}&'
            f'fields={data['fields']}&key={data['key']}&'
            f'viewpoint1={meta_data['viewpoint1']}&'
            f'viewpoint2={meta_data['viewpoint2']}&r={data['r']}'
        )

    async def _get_branches_from_api(self, url: str) -> list[dict[str, Any]]:
        """Отдаёт филиалы фирмы.

        Args:
            url (str): URL запроса фирмы.

        Returns:
            list[dict[str, Any]]: филиалы фирмы.
        """
        headers = {'User-Agent': self.USER_AGENT}
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                data = await response.json()
        return data['result']['items']

    async def _get_branches(
        self,
        firm: dict[str, Any],
        meta_data: dict[str, str],
    ) -> list[dict[str, Any]]:
        """Отдаёт филиалы.

        Args:
            firm (dict[str, Any]): URL запроса фирмы.
            meta_data (dict[str, str]): мета данные для поиска.

        Returns:
            list[dict[str, Any]]: филиалы.
        """
        branch_count = firm['org']['branch_count']
        if branch_count <= 1:
            return []
        count_page = branch_count // self.SIZE_PAGE
        if branch_count % self.SIZE_PAGE:
            count_page += 1
        urls = [
            self._get_url_branches(firm, meta_data, page)
            for page in range(1, count_page + 1)
        ]
        all_branches = []
        for branches in await asyncio.gather(
            *[self._get_branches_from_api(url) for url in urls]
        ):
            all_branches.extend(branches)
        return all_branches

    async def _get_firm_data(
        self, firm: dict[str, Any], meta_data: dict[str, str]
    ) -> dict[str, str]:
        """Отдаёт данные по фирме.

        Args:
            firm (dict[str, Any]): данные по фирме из API 2GIS.
            meta_data (dict[str, str]): meta-данные.

        Returns:
            dict[str, str]: данные по фирме.
        """
        if not self._validate_address(firm):
            return {}
        org_id = firm.get('org', {'id': None})['id']
        firm = {
            'org_id': org_id,
            'name': self._get_name(firm),
            'phone': self._get_contact(firm, 'phone'),
            'address': self._get_address(firm),
            'email': self._get_contact(firm, 'email'),
            'image_href': self._get_image(firm),
            'site': self._get_contact(firm, 'website'),
            'work_schedule': self._get_work_schedule(firm),
        }
        if self.PARSING_BRANCHES and org_id:
            firm['branches'] = await self._get_branches(firm, meta_data)
        return firm

    async def _get_firms_from_api(
        self,
        url: str,
        meta_data: dict[str, str],
    ) -> list[dict[str, str]]:
        """Отдаёт данные по фирмам из API 2GIS.

        Args:
            url (str): URL запроса страницы фирм.
            meta_data (dict[str, str]): мета данные для поиска.

        Returns:
            dict[str, str]: данные по фирмам из API 2GIS.
        """
        headers = {'User-Agent': self.USER_AGENT}
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                data = await response.json()
        firms = []
        result = data.get('result')
        if not result:
            return []
        for firm in data['result']['items']:
            firm = await self._get_firm_data(firm, meta_data)
            if firm:
                firms.append(firm)
        return firms

    async def _get_firms_data(
        self,
        meta_data: dict[str, str],
    ) -> list[dict[str, str]]:
        """Получает данные по фирмам из API.

        meta_data (dict[str, str]): мета данные для поиска.

        Returns:
            list[dict[str, str]]: список данных по фирмам.
        """
        urls = [
            self._get_url_firms_page(meta_data, page)
            for page in range(1, meta_data['count_page'] + 1)
        ]
        all_firms = []
        for firms in await asyncio.gather(
            *[self._get_firms_from_api(url, meta_data) for url in urls]
        ):
            if firms:
                all_firms.extend(firms)
        return all_firms

    def _excludes_paired_firms(
        self,
        firms: list[dict[str, Any]],
        orgs_id: set[str],
    ) -> list[dict[str, Any]]:
        """Исключает уже спаршенные фирмы.

        Args:
            firms (list[dict[str, str]]): фирмы страницы.
            orgs_id (set[str]): id спаршенных организаций.

        Returns:
            list[dict[str, Any]]: не спаршенные фирмы.
        """
        firms = [firm for firm in firms if firm['org_id'] not in orgs_id]
        no_duplicates_firms = []
        new_orgs_id = set()
        for firm in firms:
            org_id = firm['org_id']
            if org_id in new_orgs_id:
                continue
            no_duplicates_firms.append(firm)
            if org_id:
                new_orgs_id.add(org_id)
        return no_duplicates_firms

    def _get_firms(
        self,
        a_subrubric: tuple[str, str],
        orgs_id: set[str] = set(),
    ) -> tuple[list[dict[str, str]], set[str]]:
        """Отдаёт список данных по фирмам.

        Args:
            a_subrubric (tuple[str, str]):  данные по подрубрике.
            orgs_id (list[str]):  id спаршенных организаций.

        Returns:
            tuple[list[dict[str, str]], set[str]]:
             список данных по фирмам и спаршенные организации.
        """
        self._get_page_subrubric(a_subrubric[1])
        meta_data = self._get_meta_data()
        firms = asyncio.run(self._get_firms_data(meta_data))
        count_firms = len(firms)
        firms = self._excludes_paired_firms(firms, orgs_id)
        count_no_duplicates_firms = len(firms)
        count_duplicates_firms = count_firms - count_no_duplicates_firms
        orgs_id.update([firm['org_id'] for firm in firms if firm['org_id']])
        self.signal_parse_firms(
            a_subrubric[0],
            count_no_duplicates_firms,
            count_duplicates_firms,
        )
        return firms, orgs_id

    def parsing(self) -> RubricsData:
        """Полный парсинг фирм с рубриками и подрубриками.

        Returns:
            RubricsData: данных по фирмам.
        """
        a_rubrics = self._get_rubrics()
        data = {}
        all_orgs_id = set()
        for a_rubric in a_rubrics:
            rubric_name = a_rubric[0]
            data[rubric_name] = {}
            a_subrubrics = self._get_subrubrics(a_rubric)
            for a_subrubric in a_subrubrics:
                firms, orgs_id = self._get_firms(a_subrubric, all_orgs_id)
                all_orgs_id.union(orgs_id)
                data[rubric_name][a_subrubric[0]] = firms
        return data
