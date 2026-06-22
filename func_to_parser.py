import re
from read_to_config import *

def parse_tooltip(tooltip: str) -> dict | None:
    """Функция фильтрации пользователей на странице. Написано с помощью ИИ!"""
    # Пропускаем служебного пользователя
    if tooltip.startswith("jira_estimate"):
        return None
    
    # Работает ли сотрудник [X] или None 
    # Ищем прогресс в круглых скобках (0/15)
    
    # r"..." — raw string, \ не экранируется (нужно для regex)
    # \[([^\]]+)\] — ищет [что угодно] и захватывает содержимое
    # \((\d+/\d+)\) — ищет (цифра/цифра)
    # ? — означает "необязательно"
    
    pattern = r"^(.+?)(?:\s+\[([^\]]+)\])?\s+\((\d+/\d+)\)$"
    match = re.match(pattern, tooltip.strip())
    
    if not match:
        return None
    
    name     = match.group(1).strip()  # Ф.И.О
    estimate = match.group(2)          # X, или None
    progress = match.group(3)          # X/X
    
    return {
        "name": name,
        "estimate": estimate if estimate else "—",  # если None → "—"
        "progress": progress
    }


def filter_res(parsed) -> list:
    """Функция для фильтрации пользователей которые уже могут не работать и так-же люди которые не оценивают(Пелюшенко, Петухова)"""
    result_list = []

    # Список в который можно добавить людей, которые не оценивают
    dont_appreciate = [
                    "Пелюшенко Сергей Владимирович",
                    "Петухова Виктория Александровна"
                    ]
    
    for participant in parsed:
        if participant['estimate'] == 'X':
            continue
        elif participant['name'] in dont_appreciate:
            continue
        else:
            result_list.append(participant)
            
    return result_list


def filter_check(result_list) -> list:
    """Функция для фильтрации пользователей по оценкам"""
    res = []
    for names in result_list:
        current, total = map(int, names['progress'].split('/'))
        
        if current == 0:
            res.append(f"🟥 {names['name']} {names['progress']}")
        elif current < total:
            res.append(f"🟧 {names['name']} {names['progress']}")
        elif current == total:
            res.append(f"🟩 {names['name']} {names['progress']}")
    return res


def check_authorization(page):
    if "login" not in page.url and not page.locator("#login-form-username").is_visible():
        logging.info("Авторизация не требуется")
        return
    

    print("Авторизация...")
    
    logging.info("Начало авторизации")
    
    #page.goto(f"{BOARDS[0]}/login")
    #page.wait_for_selector("#login-form-username")
    
    page.fill("#login-form-username", USERNAME)
    page.fill("#login-form-password", PASSWORD)
    page.click("#login-form-submit")
    
    #page.wait_for_url("**/secure/**")
    #print(f"URL авторизован.")
    #logging.info(f"Успешная авторизация. URL: {page.url}")