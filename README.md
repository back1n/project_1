# Jira Parser (Playwright)

  

> Автоматический парсер оценки участников из доски Jira, написанный на python с использованием Playwright


## Описание

Скрипт автоматически подключается по переданным в json файле ссылкам(доскам) в Jira. Парсит данные об участниках и их оценках в проекте. Отображает результат с cmd


## Установка

1. Клонируйте репозиторий:
```bash
git clone <url-репозитория>
cd <имя-папки-проекта>
```

2. Создайте и активируйте виртуальное окружение:
```bash
python -m venv venv
source venv/bin/activate  # Для Linux/macOS
venv\Scripts\activate # Для Windows
```

4. Установите зависимости
```bash
pip install -r requirements.txt
```
 
5. Установите браузеры для Playwright:
```bash
playwright install
```


## Конфигурация


Все данные хранятся в файле config.json
```json
{
  "jira_url": "https://jira.company.ru/secure/ManageRapidViews.jspa",
  "username": "your_login",
  "password": "your_password",
  "sessions": ["session_1", "session_2", "session_3"],
  "output_format": "csv",
  "log_file": "jira_rating_check.log"
}
```

Параметры:

| Поле          | Описание                                                                           |
| ------------- | ---------------------------------------------------------------------------------- |
| jira_url      | URL страницы со всеми досками                                                      |
| username      | Логин для авторизации                                                              |
| password      | Пароль для авторизации                                                             |
| session       | Список сессий/досок для парсинга                                                   |
| output_format | Формат вывода (cvs по умолчанию). P.s пока реализовано только отображение в cmd!!! |
| log_file      | Имя файла для записи логов выполнения                                              |


В файле connect_playwright.py, по умолчанию отключено отображение работы браузера

62 строчка
```python
browser = p.chromium.launch(headless=True)
```

Для отображения окна браузера, изменить параметр на False:
```python
browser = p.chromium.launch(headless=False)
```
## Запуск

Выполните:
```bash
python connect_playwright.py
```
  
После запуска скрипт:

1. Считает настройки из config.json
2. Инициализирует логирование
3. Запустит Playwright и авторизуется в jira
4. Спарсит данные по указанным сессиям
5. Вывод информации об оценках участников
