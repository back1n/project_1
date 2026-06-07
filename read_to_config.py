import json
import logging


try:
    with open('config.json', 'r', encoding='utf-8') as file:
        data = json.load(file)

except FileNotFoundError:
    raise FileNotFoundError("Не обнаружен файл config.json")


# НАСТРОЙКА logging
LOG_FILE = data.get('log_file', 'jira_rating_check.log')
logging.basicConfig(
    filename=LOG_FILE,
    filemode='w'
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    encoding='utf-8'
)


# ПЕРЕМЕННЫЕ
try:
    JIRA_URL   = data['jira_url']  # Авторизация
    USERNAME   = data['username']  # Логин пользователя
    PASSWORD   = data['password']  # Пароль пользователя
    SESSIONS   = data['sessions']   # это список ссылок
    OUT_FORMAT = data.get('output_format', 'csv')  # необязательный параметр

    logging.info('Конфиг успешно прочитан')
    print(f"Загружено сессий: {len(SESSIONS)}")  # кол-во ссылок 

except KeyError as key:
    logging.error(f"Не обнаружен параметр {key}")
    raise KeyError(f"В config.json отсутствует обязательный параметр: {key}")



