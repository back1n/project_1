import json
import logging

# ==============================
# ЧТЕНИЕ КОНФИГА
# ==============================
try:
    with open('config.json', 'r', encoding='utf-8') as file:
        data = json.load(file)

except FileNotFoundError:
    # raise с Exception — правильный способ остановить программу с сообщением
    raise FileNotFoundError("Не обнаружен файл config.json")

# ==============================
# НАСТРОЙКА ЛОГИРОВАНИЯ
# ==============================
# Выносим отдельно — логгер нужен во всей программе
LOG_FILE = data.get('log_file', 'jira_rating_check.log')
# .get() — берёт значение по ключу, если нет — возвращает второй аргумент
# Это чище чем try/except для одного ключа

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    encoding='utf-8'
)

# ==============================
# ПЕРЕМЕННЫЕ
# ==============================
try:
    JIRA_URL   = data['jira_url']
    USERNAME   = data['username']
    PASSWORD   = data['password']
    SESSIONS   = data['sessions']   # это список ссылок
    OUT_FORMAT = data.get('output_format', 'csv')  # необязательный параметр

    logging.info('Конфиг успешно прочитан')
    print(f"Загружено сессий: {len(SESSIONS)}")  # чтобы видеть сколько ссылок

except KeyError as key:
    logging.error(f"Не обнаружен параметр {key}")
    raise KeyError(f"В config.json отсутствует обязательный параметр: {key}")



