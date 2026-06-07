import re
from read_to_config import *
from playwright.sync_api import sync_playwright

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
    """Функция для фильтрации пользователей которые уже могут не работать"""
    result_list = []
    for participant in parsed:
        if participant['estimate'] == 'X':
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


with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    try:
        # Авторизация
        print("Авторизация...")
        logging.info("Начало авторизации")
    
        page.goto(f"{JIRA_URL}/login")
        page.wait_for_selector("#login-form-username")
    
        page.fill("#login-form-username", USERNAME)
        page.fill("#login-form-password", PASSWORD)
        page.click("#login-form-submit")
    
        page.wait_for_url("**/secure/**")
        print(f"Авторизован. URL: {page.url}")
        logging.info(f"Успешная авторизация. URL: {page.url}")

        # Цикл по Доскам
        for index, session_url in enumerate(SESSIONS, start=1):
            try:
                page.goto(session_url)
                page.wait_for_load_state("networkidle")
                page.wait_for_selector(".agilepoker-iframe")

                frame = page.frame_locator(".agilepoker-iframe")
                frame.locator(".session-participants-status").wait_for()

                # Наименование проекта и доски
                header = frame.locator(".session-layout-header")
                title = header.locator(".session-layout-header-subtitle a").inner_text()
                full_text = header.inner_text()
                estimation = full_text.replace(title, "").strip()

                print(f"\n{'='*50}")
                print(f"Проект: {title}")
                print(f"Доска: {estimation}")
                print(f"{'='*50}")

                participants = frame.locator(".session-participants-status img").all()

                results = []
                for img in participants:
                    tooltip = img.get_attribute("data-tooltip")
                    if not tooltip:
                        continue
                    parsed = parse_tooltip(tooltip)
                    if parsed:
                        results.append(parsed)

                # Обрабатываем данные с сессии/доски
                res = filter_res(results)
                result = filter_check(res)
            
                print(f"\nУчастники ({len(result)}):")
                for i in result:
                    print(f"  {i}")
                
                print("Сессия обработана")
                logging.info(f"Сессия {session_url} обработана")
            except:
                print(f"Ссессия {index} не обработана. Проверьте ссылку!")
                logging.error(f"Ошибка парсинга ссылки {session_url}")
            else:
                print("\nВсе сессии обработаны!")
                logging.info("Все сессии обработаны")
    except:
        print(f"Ошибка авторизации. Проверьте ссылку {JIRA_URL} на корректность или доступность")
        logging.error(f"Ошибка авторизации {JIRA_URL}")
    
    browser.close()