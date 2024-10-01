import sys
from pathlib import Path
from os.path import join
from datetime import datetime
import json

from PyQt6 import QtWidgets, uic
from PyQt6.QtWidgets import QMainWindow, QListWidgetItem
from PyQt6.QtCore import QRegularExpression
from PyQt6.QtGui import QRegularExpressionValidator, QColor

from settings import GUISettings
from threads import (
    ParsingRubricsThread,
    ParsingFirmRubricTread,
    ParsingFirmRubricsThread,
)
from typings import RubricsData


class GUI(GUISettings):
    """Графический интерфейс парсера."""

    def _set_row_in_console(
        self,
        text: str,
        color: str | None = None,
        support_info: str = '',
    ) -> None:
        """Устанавливает строку в консоль.

        Args:
            text (str): текст строчки.
            color (str | None, optional): цвет текста. Defaults to None.
            support_info (str): вспомогательная информация.
        """

        item = QListWidgetItem(
            f'{datetime.now().strftime(self.FORMAT_TIME)} | {support_info} > '
            f'{text}'
        )
        if color:
            item.setForeground(QColor(color))
        console = self.win.console
        console.addItem(item)
        if console.count() > self.MAX_ROW_CONSOLE:
            console.takeItem(0)

    def _display_rubrics(self, data: RubricsData) -> None:
        """Выводит рубрики.

        Args:
            data (RubricsData): словарь рубрик.
        """
        self._enabled_interface(True)
        list_rubrics = self.win.list_rubrics
        list_rubrics.clear()
        self.win.parsing_firms.setEnabled(False)
        for name, values in data.items():
            item = QListWidgetItem(f'[Рубрика] {name}')
            item.is_rubric = True
            item.name = name
            item.url = values['url']
            subrubrics = values['subrubrics']
            item.subrubrics = subrubrics
            list_rubrics.addItem(item)
            for subrubric in subrubrics:
                name = subrubric['name']
                item = QListWidgetItem(f'[Подрубрика] {name}')
                item.name = name
                item.is_rubric = False
                item.url = subrubric['url']
                list_rubrics.addItem(item)

    def _enabled_interface(self, flag: bool) -> None:
        """Включение-отключение интерфейса.

        Args:
            flag (bool): флаг активности.
        """
        self.win.parsing_rubrics.setEnabled(flag)
        self.win.parsing_firms.setEnabled(flag)
        self.win.all_parsing.setEnabled(flag)
        self.win.list_rubrics.setEnabled(flag)
        self.win.name_city.setEnabled(flag)
        self.win.slug_city.setEnabled(flag)

    def _check_activity_elements(self, *arg, **kwarg) -> None:
        """Проверка активности элементов."""
        name_city = self.win.name_city
        slug_city = self.win.slug_city
        list_rubrics = self.win.list_rubrics
        parsing_firms = self.win.parsing_firms
        all_parsing = self.win.all_parsing
        parsing_rubrics = self.win.parsing_rubrics

        list_rubrics.setEnabled(True)
        name_city.setEnabled(True)
        slug_city.setEnabled(True)
        value_name = name_city.text()
        value_slug = slug_city.text()
        if value_name and value_slug:
            parsing_rubrics.setEnabled(True)
            all_parsing.setEnabled(True)
            if list_rubrics.currentItem():
                parsing_firms.setEnabled(True)
            else:
                parsing_firms.setEnabled(False)
            return
        parsing_rubrics.setEnabled(False)
        all_parsing.setEnabled(False)
        parsing_firms.setEnabled(False)

    def _change_slug_city(self, value: str) -> None:
        """Проверка изменения slug города.

        Args:
            value (str): значение поля.
        """
        list_rubrics = self.win.list_rubrics
        list_rubrics.clear()

        path_file = join('cities', value, 'rubrics.json')
        try:
            if value and Path(path_file).exists():
                with open(path_file, 'r') as file:
                    self._display_rubrics(json.load(file))
        except Exception:
            self._set_row_in_console(
                'Ошибка чтения файла рубрик',
                'red',
                'Ошибка',
            )
        self._check_activity_elements()

    def _parsing_rubrics(self) -> None:
        """Запуск парсинга рубрик."""
        self._enabled_interface(False)
        self.thread = ParsingRubricsThread(
            self._set_row_in_console,
            self.win.slug_city.text(),
            self.win.name_city.text(),
        )
        self.thread.finished.connect(self.thread.deleteLater)
        self.thread.load_finished.connect(self._display_rubrics)
        self.thread.start()

    def _parsing_firm_rubric(self) -> None:
        """Запуск парсинга фирм рубрики."""
        self._enabled_interface(False)
        self.thread = ParsingFirmRubricTread(
            self._set_row_in_console,
            self.win.list_rubrics.currentItem(),
            self.win.name_city.text(),
        )
        self.thread.finished.connect(self.thread.deleteLater)
        self.thread.load_finished.connect(self._enabled_interface)
        self.thread.start()

    def _parsing_firm_rubrics(self) -> None:
        """Парсинг фирм всех рубрик."""
        self._enabled_interface(False)
        self.thread = ParsingFirmRubricsThread(
            self._set_row_in_console,
            self.win.slug_city.text(),
            self.win.name_city.text(),
        )
        self.thread.finished.connect(self.thread.deleteLater)
        self.thread.load_finished.connect(self._check_activity_elements)
        self.thread.start()

    def _change_rubric(self) -> None:
        """Проверка изменения рубрики."""
        value_name = self.win.name_city.text()
        value_slug = self.win.slug_city.text()
        if value_name and value_slug:
            self.win.parsing_firms.setEnabled(True)

    def _set_validators(self) -> None:
        """Устанавливает валидаторы."""
        validator_name = QRegularExpressionValidator(
            QRegularExpression(self.REGULAR_NAME_CITY)
        )
        validator_slug = QRegularExpressionValidator(
            QRegularExpression(self.REGULAR_SLUG_CITY)
        )
        self.win.name_city.setValidator(validator_name)
        self.win.slug_city.setValidator(validator_slug)

    def _set_connects(self) -> None:
        """Устанавливает обработчики."""
        self.win.name_city.textChanged.connect(self._check_activity_elements)
        self.win.slug_city.textChanged.connect(self._change_slug_city)
        self.win.list_rubrics.itemSelectionChanged.connect(self._change_rubric)
        self.win.parsing_rubrics.clicked.connect(self._parsing_rubrics)
        self.win.parsing_firms.clicked.connect(self._parsing_firm_rubric)
        self.win.all_parsing.clicked.connect(self._parsing_firm_rubrics)

    def __init__(self) -> None:
        """Инициализация GUI."""
        app = QtWidgets.QApplication([])
        self.win: QMainWindow = uic.loadUi('gui.ui')
        self._set_validators()
        self._set_connects()
        Path('cities').mkdir(parents=True, exist_ok=True)
        self.win.show()
        sys.exit(app.exec())
