import sys
from pathlib import Path
from datetime import datetime

from PyQt6 import QtWidgets, uic
from PyQt6.QtWidgets import QMainWindow, QListWidgetItem
from PyQt6.QtCore import QRegularExpression
from PyQt6.QtGui import QRegularExpressionValidator, QColor

from settings import GUISettings
from threads import ParsingRubricsThread


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

    def _enabled_interface(self, flag: bool) -> None:
        """Включение-отключение интерфейса.

        Args:
            flag (bool): флаг активности.
        """
        self.win.parsing_rubrics.setEnabled(flag)
        self.win.parsing_firms.setEnabled(flag)
        self.win.all_parsing.setEnabled(flag)
        self.win.list_rubrics.setEnabled(flag)
        self.win.name_sity.setEnabled(flag)
        self.win.slug_sity.setEnabled(flag)

    def _change_sity(self, value: str) -> None:
        """Проверка изменения города.

        Args:
            value (str): значение поля.
        """
        value_name = self.win.name_sity.text()
        value_slug = self.win.slug_sity.text()
        if value_name and value_slug:
            self.win.parsing_rubrics.setEnabled(True)
            self.win.all_parsing.setEnabled(True)
            return
        self.win.parsing_rubrics.setEnabled(False)
        self.win.all_parsing.setEnabled(False)

    def _parsing_rubrics(self) -> None:
        """Запуск парсинга рубрик."""
        self._enabled_interface(False)
        self.thread = ParsingRubricsThread(
            self._set_row_in_console,
            self.win.slug_sity.text(),
            self.win.name_sity.text(),
        )
        self.thread.finished.connect(self.thread.deleteLater)
        self.thread.load_finished.connect(self._enabled_interface)
        self.thread.start()

    def _set_validators(self) -> None:
        """Устанавливает валидаторы."""
        validator_name = QRegularExpressionValidator(
            QRegularExpression(self.REGULAR_NAME_SITY)
        )
        validator_slug = QRegularExpressionValidator(
            QRegularExpression(self.REGULAR_SLUG_SITY)
        )
        self.win.name_sity.setValidator(validator_name)
        self.win.slug_sity.setValidator(validator_slug)

    def _set_connects(self) -> None:
        """Устанавливает обработчики."""
        self.win.name_sity.textChanged.connect(self._change_sity)
        self.win.slug_sity.textChanged.connect(self._change_sity)
        self.win.parsing_rubrics.clicked.connect(self._parsing_rubrics)

    def __init__(self) -> None:
        """Инициализация GUI."""
        app = QtWidgets.QApplication([])
        self.win: QMainWindow = uic.loadUi('gui.ui')
        self._set_validators()
        self._set_connects()
        Path('cities').mkdir(parents=True, exist_ok=True)
        self.win.show()
        sys.exit(app.exec())


GUI()
