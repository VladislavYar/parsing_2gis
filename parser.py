from urllib.parse import urljoin
from typing import Any

from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions
from selenium.webdriver import Chrome, ChromeOptions
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import (
    NoSuchElementException,
    JavascriptException,
    TimeoutException,
)

from settings import ParserSettings


class Parser(ParserSettings):
    """Парсер фирм в 2gis."""

    def __init__(self) -> None:
        """Инициализация драйвера парсера."""
        options = ChromeOptions()
        options.add_argument(self.LOG_LEVEL)
        service = Service(executable_path=ChromeDriverManager().install())
        self.driver = Chrome(options=options, service=service)

    def _waiting_element(self, time: int | float, selector: str) -> None:
        """Ожидание элемента.

        Args:
            time (int): время ожидания.
            selector (str): селектор элемента.
        """
        WebDriverWait(self.driver, time).until(
            expected_conditions.presence_of_element_located(
                (
                    By.CSS_SELECTOR,
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
                f'{urljoin(self.WEBSITE, self.SLUG_SITY)}/',
                self.SLUG_RUBRICS,
            )
        )
        if self.SLUG_SITY not in self.driver.current_url:
            return []
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
            self._waiting_element(1, selector)
            a_subrubrics = self.driver.find_elements(By.CSS_SELECTOR, selector)
        else:
            selector = (
                f'.{self.CLASS_CONTENT_BLOCK}:nth-child(2) '
                f'a.{self.CLASS_SUBRUBRICS}'
            )
            try:
                self._waiting_element(1, selector)
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

    def _validate_address(self, firm: WebElement) -> bool:
        """Вадилация адреса.

        Args:
            firm (WebElement): блок с фирмой.

        Returns:
            bool: флаг валидации.
        """
        selector = (
            f'span.{self.CLASS_ADDRESS_BLOCK} '
            f'span.{self.CLASS_ADDRESS}:first-child'
        )
        try:
            address = (
                firm.find_element(By.CSS_SELECTOR, selector)
                .get_attribute('textContent')
                .strip()
            )
            if self.VALIDATE_NAME_CITY not in address:
                return False
            return True
        except NoSuchElementException:
            return False

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
                if contact['type'] == key:
                    url = contact.get('url')
                    if url:
                        return url
                    value = contact['value']
                    if key == 'phone' and value[0] == '8':
                        return f'+7{value[1:]}'
                    return value
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

    def _get_firm_id(self, firm: WebElement) -> str:
        """Отдаёт id фирмы

        Args:
            firm (WebElement): блок с фирмой.

        Returns:
            str: id фирмы.
        """
        selector = f'div .{self.CLASS_NAME_BLOCK} a'
        href = firm.find_element(By.CSS_SELECTOR, selector).get_attribute(
            'href'
        )
        return href.split('firm/')[-1].split('?')[0].strip()

    def _get_firm_data(self, firm_id: str) -> dict[str, Any]:
        """Отдаёт словарь данных по фирме.

        Args:
            firm_id (str): id фирмы.

        Returns:
            dict[str, Any]: словарь данных по фирме.
        """
        firm_data = self.driver.execute_script(
            f'return initialState.data.entity.profile["{firm_id}"].data;'
        )
        return firm_data

    def _get_firm_link(self, firm_id: str) -> str:
        """Отдаёт ссылку на фирму.

        Args:
            firm_id (str): id фирмы.

        Returns:
            str: ссылка на фирму.
        """
        return urljoin(
            urljoin(
                f'{urljoin(self.WEBSITE, self.SLUG_SITY)}/',
                f'{self.SLUG_FIRM}/',
            ),
            firm_id,
        )

    def _open_window_firm(self, firm_id: str) -> str:
        """Открывает фирму в новом окне.

        Args:
            firm_id (str): id фирмы.

        Returns:
            str: предыдущие окно в браузере.
        """
        window_before = self.driver.window_handles[0]
        url = self._get_firm_link(firm_id)
        self.driver.execute_script(f'window.open("{url}","_blank");')
        window_after = self.driver.window_handles[1]
        self.driver.switch_to.window(window_after)
        return window_before

    def _get_data_firms(self) -> list[dict[str, str]]:
        """Получает данные по фирмам.

        Returns:
            list[dict[str, str]]: список данных по фирмам.
        """
        selector = f'.{self.CLASS_FIRM_BLOCK} div.{self.CLASS_FIRM}'
        firms = []
        for firm in self.driver.find_elements(By.CSS_SELECTOR, selector):
            if not self._validate_address(firm):
                continue

            firm_id = self._get_firm_id(firm)
            window_before = self._open_window_firm(firm_id)
            firm_data = self._get_firm_data(firm_id)

            name = firm_data['name_ex']['primary']
            address = self._get_address(firm_data)
            work_schedule = self._get_work_schedule(firm_data)
            image = self._get_image(firm_data)
            email = self._get_contact(firm_data, 'email')
            site = self._get_contact(firm_data, 'website')
            phone = self._get_contact(firm_data, 'phone')
            firms.append(
                {
                    'name': name,
                    'phone': phone,
                    'address': address,
                    'email': email,
                    'image_href': image,
                    'site': site,
                    'work_schedule': work_schedule,
                    'link': self._get_firm_link(firm_id),
                }
            )

            self.driver.execute_script('window.close()')
            self.driver.switch_to.window(window_before)
        return firms

    def _get_firms(self, a_subrubric: tuple[str, str]) -> list[dict[str, str]]:
        """Отдаёт список данных по фирмам.

        Args:
            a_subrubric (tuple[str, str]):  данные по подрубрике.

        Returns:
            list[dict[str, str]]: список данных по фирмам.
        """
        firms = []
        self.driver.get(a_subrubric[1])
        firms.extend(self._get_data_firms())
        selector = f'div.{self.CLASS_NEXT_PAGE_FIRMS}:last-child'
        try:
            while True:
                self.driver.execute_script(
                    f'let element = document.querySelector("{selector}");'
                    'element.click();'
                )
                self._waiting_element(1, f'div.{self.CLASS_FIRM_BLOCK}')
                firms.extend(self._get_data_firms())
        except JavascriptException:
            return firms

    def parsing(self) -> list:
        """Полный парсинг фирм с рубриками и подрубриками.

        Returns:
            list: возвращает список данных по фирмам.
        """
        a_rubrics = self._get_rubrics()
        data = {}
        for a_rubric in a_rubrics:
            data[a_rubric[0]] = {}
            a_subrubrics = self._get_subrubrics(a_rubric)
            for a_subrubric in a_subrubrics:
                firms = self._get_firms(a_subrubric)
                data[a_rubric[0]][a_subrubric[0]] = firms
        return data
