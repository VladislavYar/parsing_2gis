from pathlib import Path
from os.path import join
from typing import Any
import json

from PyQt6.QtCore import pyqtSignal, QThread
from PyQt6.QtWidgets import QListWidgetItem
import requests
from requests.exceptions import ConnectionError

from parser import Parser
from typings import RubricsData, FirmRubricData, FirmSubrubricData
from exceptions import NoCityOn2GISException


class SendFirmsToServerThread(QThread):
    """Поток отправки фирм на сервер."""

    load_finished = pyqtSignal(object)

    def __init__(
        self,
        firms: list[dict[str, str]],
        slug_city: str,
        slug_rubric: str,
        url_api: str,
        set_message_save_form: Any,
        auth_data: str | None = None,
    ) -> None:
        """Инициализация потока

        Args:
            firms (list[dict[str, str]]): фирмы.
            slug_city (str): slug города на сервере.
            slug_rubric (str): slug рубрики на сервере.
            url_api (str): URL API для отправки данных.
            set_message_save_form (Any): метод установки сообщения.
            auth_data (str | None, optional):
                Данные аутентификации. Defaults to None.
        """
        super().__init__()
        self.firms = firms
        self.slug_city = slug_city
        self.slug_rubric = slug_rubric
        self.url_api = url_api
        self.set_message_save_form = set_message_save_form
        self.auth_data = auth_data

    def _send_firms(self) -> None:
        """Отправка фирм на сервер."""
        headers = None
        if self.auth_data:
            headers = {'Authorization': self.auth_data}
        try:
            response = requests.post(
                self.url_api,
                headers=headers,
                json={
                    'firms': self.firms,
                    'city': self.slug_city,
                    'rubric': self.slug_rubric,
                },
            )
            if response.status_code == 201:
                self.set_message_save_form('Фирмы загружаются', 3, 'green')
            elif response.status_code == 400:
                self.set_message_save_form('Ошибка валидации', 3, 'red')
            elif response.status_code == 401:
                self.set_message_save_form('Ошибка аутентификации', 3, 'red')
            else:
                self.set_message_save_form(
                    'Ошибка, попробуйте позже',
                    3,
                    'red',
                )
        except ConnectionError:
            self.set_message_save_form('Ошибка соединения', 3, 'red')

    def run(self) -> None:
        """Запуск потока."""
        self._send_firms()
        self.load_finished.emit(True)


class BaseParsingTread(QThread):
    """Базовый поток для парсинга."""

    load_finished = pyqtSignal(object)

    def _message_parse_firms(
        self,
        name_subrubric: str,
        count_no_duplicates_firms: int,
        count_duplicates_firms: int,
    ) -> None:
        """Сообщение о парсинге фирм.

        Args:
            name_subrubric (str): название подрубрики
            count_no_duplicates_firms (int): кол-во фирм без дубликатов.
            count_duplicates_firms (int): количество дубликатов.
        """

        self.set_row_in_console(
            f'Сохранено фирм: {count_no_duplicates_firms}, '
            f'удалено дубликатов: {count_duplicates_firms}',
            support_info=f'Парсинг фирм [{name_subrubric}]',
        )

    def _save_data(
        self,
        name_file: str,
        message_console: str,
        data: Any,
    ) -> None:
        """Сохраняет данные.

        Args:
            name_file (str): название файла.
            message_console (str): сообщение в консоль.
            data (Any): данные для сохранения.
        """
        city_dir = join('cities', self.parser.SLUG_CITY)
        Path(city_dir).mkdir(
            parents=True,
            exist_ok=True,
        )
        with open(
            join(city_dir, f'{name_file.replace('/', '')}.json'), 'w'
        ) as file:
            json.dump(data, file)
        self.set_row_in_console(message_console, 'green', self.support_info)


class ParsingFirmRubricTread(BaseParsingTread):
    """Поток для парсинга фирм рубрики."""

    support_info = 'Парсинг фирм'

    def __init__(
        self,
        set_row_in_console: Any,
        rubric: QListWidgetItem,
        slug_city: str,
        validate_name_city: str,
    ) -> None:
        """Инициализация потока.

        Args:
            set_row_in_console (Any): метод установки строчки в консоль.
            rubric (QListWidgetItem): выбранная рубрика.
            validate_name_city (str): название города.
        """
        super().__init__()
        self.set_row_in_console = set_row_in_console
        self.rubric = rubric
        self.parser = Parser()
        self.parser.signal_parse_firms = self._message_parse_firms
        self.parser.VALIDATE_NAME_CITY = validate_name_city
        self.parser.SLUG_CITY = slug_city

    def _parsing_subrubric_firm(self) -> tuple[str, FirmSubrubricData]:
        """Парсинг фирм подрубрики.

        Returns:
            tuple[str, FirmSubrubricData]: название и фирмы подрубрики.
        """

        name = self.rubric.name
        self.set_row_in_console(
            f'Запуск парсинга фирм подрубрики "{name}"',
            'blue',
            self.support_info,
        )
        firms, _ = self.parser._get_firms((name, self.rubric.url))
        self.set_row_in_console(
            f'Конец парсинга фирм подрубрики "{name}"',
            'blue',
            self.support_info,
        )
        return (name, {'firms': firms})

    def _parsing_rubric_firm(self) -> tuple[str, FirmRubricData]:
        """Парсинг фирм рубрики.

        Returns:
            tuple[str, FirmRubricData]: название и фирмы рубрики.
        """
        rubric_name = self.rubric.name
        self.set_row_in_console(
            f'Запуск парсинга фирм рубрики "{rubric_name}"',
            'blue',
            self.support_info,
        )
        data = {'subrubrics': []}
        for subrubric in self.rubric.subrubrics:
            name = subrubric['name']
            self.set_row_in_console(
                f'Старт парсинга фирм подрубрики "{name}"',
                support_info=self.support_info,
            )
            firms, _ = self.parser._get_firms((name, subrubric['url']))
            data['subrubrics'].append({name: firms})
            self.set_row_in_console(
                f'Конец парсинга фирм подрубрики "{name}"',
                support_info=self.support_info,
            )
        self.set_row_in_console(
            f'Конец парсинга фирм рубрики "{rubric_name}"',
            'blue',
            self.support_info,
        )
        return rubric_name, data

    def run(self) -> None:
        """Запуск потока."""
        try:
            if self.rubric.is_rubric:
                name, data = self._parsing_rubric_firm()
                for subrubrics in data.values():
                    for subrubric in subrubrics:
                        name = list(subrubric.keys())[0]
                        self._save_data(
                            name,
                            f'Фирмы рубрики "{name}" сохранены',
                            {'firms': subrubric[name]},
                        )
            else:
                name, data = self._parsing_subrubric_firm()
                self._save_data(
                    name, f'Фирмы рубрики "{name}" сохранены', data
                )
        except Exception as e:
            self.set_row_in_console(
                f'Лог: {e}',
                'red',
                'Ошибка',
            )
            self.set_row_in_console(
                'Повторите попытку',
                'red',
                'Ошибка',
            )
        self.load_finished.emit(True)
        self.parser.driver.close()


class ParsingFirmRubricsThread(BaseParsingTread):
    """Поток для парсинга фирм всех рубрик."""

    support_info = 'Парсинг фирм'

    def __init__(
        self,
        set_row_in_console: Any,
        slug_city: str,
        validate_name_city: str,
    ) -> None:
        """Инициализация потока.

        Args:
            set_row_in_console (Any): метод установки строчки в консоль.
            slug_city (str): slug города.
            validate_name_city (str): название города.
        """
        super().__init__()
        self.set_row_in_console = set_row_in_console
        self.parser = Parser()
        self.parser.signal_parse_firms = self._message_parse_firms
        self.parser.SLUG_CITY = slug_city
        self.parser.VALIDATE_NAME_CITY = validate_name_city

    def run(self) -> None:
        """Запуск потока."""
        try:
            self.set_row_in_console(
                'Запуск парсинга фирм всех рубрик',
                'blue',
                self.support_info,
            )
            data = self.parser.parsing()
            self.set_row_in_console(
                'Конец парсинга фирм всех рубрик',
                'blue',
                self.support_info,
            )
            for subrubrics in data.values():
                for name, firms in subrubrics.items():
                    self._save_data(
                        name,
                        f'Фирмы рубрики "{name}" сохранены',
                        {'firms': firms},
                    )
            self.load_finished.emit(None)
        except NoCityOn2GISException:
            self.set_row_in_console(
                'Город с таким slug не существует',
                'red',
                'Ошибка',
            )
            self.load_finished.emit(None)
        except Exception as e:
            self.set_row_in_console(
                f'Лог: {e}',
                'red',
                'Ошибка',
            )
            self.set_row_in_console(
                'Повторите попытку',
                'red',
                'Ошибка',
            )
            self.load_finished.emit(None)
        self.parser.driver.close()


class ParsingRubricsThread(BaseParsingTread):
    """Поток для парсинга рубрик."""

    support_info = 'Парсинг рубрик'

    def __init__(
        self,
        set_row_in_console: Any,
        slug_city: str,
        validate_name_city: str,
    ) -> None:
        """Инициализация потока.

        Args:
            set_row_in_console (Any): метод установки строчки в консоль.
            slug_city (str): slug города.
            validate_name_city (str): название города.
        """
        super().__init__()
        self.set_row_in_console = set_row_in_console
        self.parser = Parser()
        self.parser.SLUG_CITY = slug_city
        self.parser.VALIDATE_NAME_CITY = validate_name_city

    def _get_data(self) -> RubricsData:
        """Отдаёт данные по рубрикам.

        Returns:
            RubricsData: данные по рубрикам.
        """
        self.set_row_in_console(
            'Запуск парсинга рубрик',
            'blue',
            self.support_info,
        )
        data = {}
        for a_rubric in self.parser._get_rubrics():
            name = a_rubric[0]
            self.set_row_in_console(
                f'Старт парсинга рубрики "{name}"',
                support_info=self.support_info,
            )
            data[name] = {'url': a_rubric[1], 'subrubrics': []}
            for a_subrubric in self.parser._get_subrubrics(a_rubric):
                data[name]['subrubrics'].append(
                    {
                        'name': a_subrubric[0],
                        'url': a_subrubric[1],
                    }
                )
            self.set_row_in_console(
                f'Конец парсинга рубрики "{name}"',
                support_info=self.support_info,
            )
        self.set_row_in_console(
            'Конец парсинга рубрик',
            'blue',
            self.support_info,
        )
        return data

    def run(self) -> None:
        """Запуск потока."""
        try:
            data = self._get_data()
            self._save_data('rubrics', 'Рубрики сохранены', data)
            self.load_finished.emit(data)
        except NoCityOn2GISException:
            self.set_row_in_console(
                'Город с таким slug не существует',
                'red',
                'Ошибка',
            )
            self.load_finished.emit({})
        except Exception as e:
            self.set_row_in_console(
                f'Лог: {e}',
                'red',
                'Ошибка',
            )
            self.set_row_in_console(
                'Повторите попытку',
                'red',
                'Ошибка',
            )
            self.load_finished.emit({})
        self.parser.driver.close()
