import re
from read_to_config import *
from playwright.sync_api import sync_playwright

def parse_tooltip(tooltip: str) -> dict | None:
    # Пропускаем служебного пользователя
    if tooltip.startswith("jira_estimate"):
        return None
    
    # Ищем оценку в квадратных скобках [X] или [5] — необязательный блок
    # Ищем прогресс в круглых скобках (0/15)
    
    # r"..." — raw string, \ не экранируется (нужно для regex)
    # \[([^\]]+)\] — ищет [что угодно] и захватывает содержимое
    # \((\d+/\d+)\) — ищет (цифра/цифра)
    # ? — означает "необязательно"
    
    pattern = r"^(.+?)(?:\s+\[([^\]]+)\])?\s+\((\d+/\d+)\)$"
    match = re.match(pattern, tooltip.strip())
    
    if not match:
        return None
    
    name     = match.group(1).strip()  # Горемыкин Олег Олегович
    estimate = match.group(2)          # X, 5, None если не проголосовал
    progress = match.group(3)          # 0/15
    
    return {
        "name": name,
        "estimate": estimate if estimate else "—",  # если None → "—"
        "progress": progress
    }


def filter_res(parsed) -> list:
    result_list = []
    for participant in parsed:
        if participant['estimate'] == 'X':
            continue
        else:
            result_list.append(participant)
            
    return result_list


def filter_check(result_list) -> list:
    res = []
    for names in result_list:
        # Правильно разбиваем "0/15" → [0, 15]
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

    # --- АВТОРИЗАЦИЯ (один раз) ---
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

    # --- ЦИКЛ ПО ССЫЛКАМ ---
    # enumerate даёт порядковый номер — удобно для логов
    for index, session_url in enumerate(SESSIONS, start=1):
            page.goto(session_url)
            page.wait_for_load_state("networkidle")
            page.wait_for_selector(".agilepoker-iframe")

            frame = page.frame_locator(".agilepoker-iframe")
            frame.locator(".session-participants-status").wait_for()

            # Заголовок
            header = frame.locator(".session-layout-header")
            title = header.locator(".session-layout-header-subtitle a").inner_text()
            full_text = header.inner_text()
            estimation = full_text.replace(title, "").strip()

            print(f"\n{'='*50}")
            print(f"Доска: {title}")
            print(f"Задача: {estimation}")
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

            # ← внутри цикла — обрабатываем каждую сессию
            res = filter_res(results)
            result = filter_check(res)
            
            print(f"\nУчастники ({len(result)}):")
            for i in result:
                print(f"  {i}")

    print("\nВсе сессии обработаны!")
    logging.info("Все сессии обработаны")
    
    browser.close()