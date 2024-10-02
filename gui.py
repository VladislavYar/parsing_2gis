import sys
from pathlib import Path
from os.path import join
from datetime import datetime
import json
import re
from typing import Any
from time import sleep
from threading import Thread

from PyQt6 import QtWidgets, uic
from PyQt6.QtWidgets import QMainWindow, QListWidgetItem, QFileDialog
from PyQt6.QtCore import QRegularExpression
from PyQt6.QtGui import QRegularExpressionValidator, QColor

from settings import GUISettings
from threads import (
    ParsingRubricsThread,
    ParsingFirmRubricTread,
    ParsingFirmRubricsThread,
    SendFirmsToServerThread,
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

    def _enabled_interface_save_form(self, flag: bool) -> None:
        """Включение-отключение интерфейса сохранения фирм.

        Args:
            flag (bool): флаг активности.
        """
        self.save_form.url_api.setEnabled(flag)
        self.save_form.auth_data.setEnabled(flag)
        self.save_form.save_settings.setEnabled(flag)
        self.save_form.set_file.setEnabled(flag)
        self.save_form.slug_rubric.setEnabled(flag)
        self.save_form.slug_city.setEnabled(flag)
        self.save_form.send_rubric.setEnabled(flag)

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
            self.win.slug_city.text(),
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
            QRegularExpression(self.REGULAR_SLUG)
        )
        validate_url = QRegularExpressionValidator(
            QRegularExpression(self.REGULAR_URL)
        )
        self.win.name_city.setValidator(validator_name)
        self.win.slug_city.setValidator(validator_slug)
        self.save_form.slug_rubric.setValidator(validator_slug)
        self.save_form.slug_city.setValidator(validator_slug)
        self.save_form.url_api.setValidator(validate_url)

    def _show_save_form(self) -> None:
        """Выводит форму сохранения фирм на сервер."""
        self.save_form.show()

    def _change_url_api(self, value: str) -> None:
        """Проверка изменения URL API.

        Args:
            value (str): значение поля.
        """
        pattern = re.compile(self.REGULAR_URL)
        flag = len(value) > 0 and bool(pattern.match(value))
        self.save_form.save_settings.setEnabled(flag)
        self._check_activity_button_send_rubric()

    @staticmethod
    def _hide_element_after_time(element: Any, time: int) -> None:
        """Скрывает элемент через определённое время.

        Args:
            element (Any): элемент.
            time (int): время.
        """
        sleep(time)
        element.hide()

    def _display_element_for_time(self, element: Any, time: int) -> None:
        """Выводит элемент на определённое время.

        Args:
            element (Any): элемент.
            time (int): время.
        """
        element.show()
        thread = Thread(
            target=GUI._hide_element_after_time,
            args=(element, time),
        )
        thread.start()

    def _set_message_save_form(
        self,
        text: str,
        timer: int,
        color: str | None = None,
    ) -> None:
        """Устанавливает сообщение в форме сохранения фирм.

        Args:
            text (str): сообщение.
            timer (int): время сообщения.
            color (str | None, optional): цвет сообщения. Defaults to None.
        """
        message_save_form = self.save_form.message_save_form
        message_save_form.setText(text)
        if color:
            message_save_form.setStyleSheet(f'color: {color}')
        else:
            message_save_form.setStyleSheet('color: none')
        self._display_element_for_time(
            message_save_form,
            timer,
        )

    def _save_settings(self) -> None:
        """Сохранение настроек."""
        settings = {
            'URL_API': self.save_form.url_api.text(),
            'AUTH_DATA': self.save_form.auth_data.text(),
        }
        with open('settings.json', 'w') as file:
            json.dump(settings, file)
        self._set_message_save_form(
            'Настройки сохранены',
            3,
            'green',
        )

    def _set_settings(self) -> None:
        """Устанавливает данные из настроек."""
        if not Path('settings.json').exists():
            return
        try:
            with open('settings.json', 'r') as file:
                settings = json.load(file)
                if not isinstance(settings, dict):
                    return
                url_api = settings.get('URL_API', '')
                pattern = re.compile(self.REGULAR_URL)
                url_api = url_api if pattern.match(url_api) else ''
                auth_data = settings.get('AUTH_DATA', '')
                self.save_form.url_api.setText(url_api)
                self.save_form.auth_data.setText(auth_data)
                self._change_url_api(url_api)
        except json.decoder.JSONDecodeError:
            return

    def _display_file_dialog(self) -> None:
        """Открывает диалоговое окно выбора json файла."""
        file_name, _ = QFileDialog.getOpenFileName(
            caption='Open Image',
            filter='*.json',
        )
        if not file_name:
            return
        if file_name.split('.')[-1] != 'json':
            return
        self.save_form.path_file.setText(file_name)
        self._check_activity_button_send_rubric()

    def _check_activity_button_send_rubric(self, *arg, **kwarg) -> None:
        """Проверка активности кнопки отправки данных по фирмам."""
        rubric = self.save_form.slug_rubric.text()
        city = self.save_form.slug_city.text()
        file_path = self.save_form.path_file.text()
        url_api = self.save_form.url_api.text()
        self.save_form.send_rubric.setEnabled(
            all((rubric, city, file_path, url_api))
        )

    def _validate_field(
        self,
        data: str | None,
        max_length: int | None = None,
        regular: str = r'.*',
        required: bool = False,
    ):
        if (
            (not data and required)
            or (data and not isinstance(data, str))
            or (None not in (data, max_length) and len(data) > max_length)
            or (data and not re.compile(regular).match(data))
        ):
            return False
        return True

    def _validate_work_schedule(
        self,
        work_schedule: dict[dict[str, str]] | None,
    ) -> bool:
        """Валидация расписания.

        Args:
            work_schedule (dict[dict[str, str]] | None): расписание.

        Returns:
            bool: флаг валидности данных.
        """
        if work_schedule is None:
            return True
        if not isinstance(work_schedule, dict):
            return False
        for key, value in work_schedule.items():
            if key not in self.KEY_DAY or not isinstance(value, dict):
                return False
            times = (value.get('from'), value.get('to'))
            pattern = re.compile(self.REGULAR_WORK_SCHEDULE)
            if not all(times) or not all(
                [pattern.match(time) for time in times]
            ):
                return False
        return True

    def _validate_firm(self, firm: dict[str, str]) -> bool:
        """Валидация фирмы.

        Args:
            firm (dict[str, str]): данные по фирме.

        Returns:
            bool: флаг валидности данных.
        """
        return_validate = (
            self._validate_field(
                firm.get('name'),
                self.MAX_LEN_NAME,
                required=True,
            ),
            self._validate_field(
                firm.get('phone'), regular=self.REGULAR_PHONE
            ),
            self._validate_field(firm.get('address'), self.MAX_LEN_ADDRESS),
            self._validate_field(
                firm.get('email'),
                self.MAX_LEN_EMAIL,
                self.REGULAR_EMAIL,
            ),
            self._validate_field(
                firm.get('image_href'),
                self.MAX_LEN_IMAGE_HREF,
                self.REGULAR_URL,
            ),
            self._validate_field(
                firm.get('site'),
                self.MAX_LEN_SITE,
                self.REGULAR_URL,
            ),
            self._validate_work_schedule(firm.get('work_schedule')),
        )
        return all(return_validate)

    def _validate_firms(self, data: dict[str, list[dict[str, str]]]) -> bool:
        """Валидация фирм.

        Returns:
            bool: флаг валидности данных.
        """
        if not isinstance(data, dict):
            return False
        firms = data.get('firms')
        if not firms:
            return False
        for firm in firms:
            if not self._validate_firm(firm):
                return False
        return True

    def _get_firms_in_file(self) -> list[dict[str, str]] | None:
        """Отдаёт фирмы из файла.

        Returns:
            list[dict[str, str]]: список фирм.
        """
        file_path = self.save_form.path_file.text()
        if not Path(file_path).exists():
            self._set_message_save_form(
                'Файл не найден',
                3,
                'red',
            )
        try:
            with open(file_path, 'r') as file:
                data = json.load(file)
                if not self._validate_firms(data):
                    self._set_message_save_form(
                        'Невалидные данные',
                        3,
                        'red',
                    )
                return data['firms']
        except json.decoder.JSONDecodeError:
            self._set_message_save_form(
                'Ошибка чтения файла',
                3,
                'red',
            )

    def _send_firms_rubric(self) -> None:
        """Отправляет фирмы рубрики на сервер."""
        firms = self._get_firms_in_file()
        if firms is None:
            return
        self._enabled_interface_save_form(False)
        self.thread_send_firms = SendFirmsToServerThread(
            firms,
            self.save_form.slug_city.text(),
            self.save_form.slug_rubric.text(),
            self.save_form.url_api.text(),
            self._set_message_save_form,
            self.save_form.auth_data.text(),
        )
        self.thread_send_firms.finished.connect(
            self.thread_send_firms.deleteLater
        )
        self.thread_send_firms.load_finished.connect(
            self._enabled_interface_save_form
        )
        self.thread_send_firms.start()

    def _set_connects(self) -> None:
        """Устанавливает обработчики."""
        self.win.name_city.textChanged.connect(self._check_activity_elements)
        self.win.slug_city.textChanged.connect(self._change_slug_city)
        self.win.list_rubrics.itemSelectionChanged.connect(self._change_rubric)
        self.win.parsing_rubrics.clicked.connect(self._parsing_rubrics)
        self.win.parsing_firms.clicked.connect(self._parsing_firm_rubric)
        self.win.all_parsing.clicked.connect(self._parsing_firm_rubrics)
        self.win.send_server.triggered.connect(self._show_save_form)

        self.save_form.url_api.textChanged.connect(self._change_url_api)
        self.save_form.save_settings.clicked.connect(self._save_settings)
        self.save_form.set_file.clicked.connect(self._display_file_dialog)
        self.save_form.send_rubric.clicked.connect(self._send_firms_rubric)
        self.save_form.slug_rubric.textChanged.connect(
            self._check_activity_button_send_rubric
        )
        self.save_form.slug_city.textChanged.connect(
            self._check_activity_button_send_rubric
        )

    def __init__(self) -> None:
        """Инициализация GUI."""
        app = QtWidgets.QApplication([])
        self.win: QMainWindow = uic.loadUi('gui.ui')
        self.save_form: QMainWindow = uic.loadUi('save_form.ui')
        self._set_validators()
        self._set_connects()
        self._set_settings()
        Path('cities').mkdir(parents=True, exist_ok=True)
        self.win.show()
        sys.exit(app.exec())
