<div align="center">
  <h1>Парсер 2GIS</h1>
  <h3>Описание</h3>
  <p>Парсер 2GIS с графическим интерфейсом и функционалом отправки данных на сервер.</p>
  <hr>
  <h3>Фукционал</h3>
  <ul>
    <li>Парсинг рубрик/подрубрик, фирм рубрики/подрубрики или данные со всего населённого пункта</li>
    <li>Указание проверочного названия города, указание slug-города для парсинга, выбор рубрики/подрубрики</li>
    <li>Виджет сохранения данных на сервер с указанием URL API, данных аутентификации, выбора файла, указания slug-рубрики и города для сохранения</li>
    <li>Сохранение рубрик/подрубрик, фирм рубрики/подрубрики, данные со всего населённого пункта и настроек в JSON-файлы и автоматическое "поддтягивание" их в GUI.</li>
  </ul>
  <hr>
  <h3>Примечания</h3>
</div>
  <p align="center">Все команды выполнять из корневой папки проекта.</p>
<hr>

<h3 align="center">Как запустить</h3>
<details>
  <p align="center"><summary align="center"><ins>Через консоль</ins></summary></p>
  <ul>
    <li align="center"><b>1.</b> Создать и активировать виртуальное окружение при помощи <code>Poetry</code>:
       <ul>
          <li><b>a)</b> Установить <code>Poetry</code>: <code>pip install poetry</code></li>
          <li><b>б)</b> Активировать виртуальное окружение: <code>poetry shell</code> (если <code>Poetry</code> не находит <code>Python ^3.11</code>, воспользоваться <a href="https://python-poetry.org/docs/managing-environments/">инструкцией</a>)</li>
          <li><b>в)</b> Установить зависимости: <code>poetry install</code></li>
       </ul>
    </li>
    <li align="center">
       <p><b>2.</b> Инициализировать <code>pre-commit</code>: <code>pre-commit install</code></p>
    </li>
    <li align="center">
      <p><b>3.</b> Выполнить команду <code>python main.py -g (--gui)</code></p>
    </li>
  </ul>
</details>

<hr>

<h3 align="center">Стек</h3>
<p align="center">
  <img src="https://img.shields.io/badge/Python-3.12-red?style=flat&logo=python&logoColor=white">
  <img src="https://img.shields.io/badge/PyQt-6-red?style=flat&logo=qt&logoColor=white">
  <img src="https://img.shields.io/badge/selenium-4.25.0-red?style=flat&logo=selenium&logoColor=white">
  <img src="https://img.shields.io/badge/aiohttp-3.10.10-red?style=flat&logo=aiohttp&logoColor=white">
  <img src="https://img.shields.io/badge/Poetry-Latest-red?style=flat&logo=poetry&logoColor=white">
  <img src="https://img.shields.io/badge/Pre commit-Latest-red?style=flat&logo=Precommit&logoColor=white">
</p>
<hr>
