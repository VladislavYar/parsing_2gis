from pathlib import Path
from os.path import join
from typing import Any
import json

from PyQt6.QtCore import pyqtSignal, QThread

from parser import Parser


class ParsingRubricsThread(QThread):
    """Поток для парсинга рубрик."""

    load_finished = pyqtSignal(object)

    def __init__(
        self,
        set_row_in_console: Any,
        slug_sity: str,
        validate_name_city: str,
    ) -> None:
        """Инициализация потока.

        Args:
            set_row_in_console (Any): метод установки строчки в консоль.
            slug_sity (str): slug города.
            validate_name_city (str): название города.
        """
        super().__init__()
        self.set_row_in_console = set_row_in_console
        self.parser = Parser()
        self.parser.SLUG_SITY = slug_sity
        self.parser.VALIDATE_NAME_CITY = validate_name_city

    def _get_data(self) -> dict[str, list[dict[str, str]]]:
        """Отдаёт данные по рубрикам.

        Returns:
            dict[str, list[dict[str, str]]]: данные по рубрикам.
        """
        support_info = 'Парсинг рубрик'
        self.set_row_in_console('Запуск парсинга рубрик', 'blue', support_info)
        data = {}
        for a_rubric in self.parser._get_rubrics():
            name = a_rubric[0]
            self.set_row_in_console(
                f'Старт парсинга рубрики "{name}"',
                support_info=support_info,
            )
            data[name] = []
            for a_subrubric in self.parser._get_subrubrics(a_rubric):
                data[name].append(
                    {
                        'name': a_subrubric[0],
                        'url': a_subrubric[1],
                    }
                )
            self.set_row_in_console(
                f'Конец парсинга рубрики "{name}"',
                support_info=support_info,
            )
        self.set_row_in_console('Конец парсинга рубрик', 'blue', support_info)
        self.parser.driver.close()
        return data

    def _save_data(self, data: dict[str, list[dict[str, str]]]) -> None:
        """Сохраняет данные по рубрикам.

        Args:
            data (dict[str, list[dict[str, str]]]): данные по рубрикам.
        """
        city_dir = join('cities', self.parser.SLUG_SITY)
        Path(city_dir).mkdir(
            parents=True,
            exist_ok=True,
        )
        with open(join(city_dir, 'rubrics.json'), 'w') as file:
            json.dump(data, file)
        self.set_row_in_console('Рубрики сохранены', 'green', 'Парсинг рубрик')

    def run(self) -> None:
        """Запуск потока."""
        data = self._get_data()
        self._save_data(self._get_data())
        self.load_finished.emit(data)
