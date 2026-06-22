from parser_board import *
from playwright.sync_api import sync_playwright


with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()

    # Цикл по Доскам
    for index, session_url in enumerate(res_session, start=1):
        
        try:
            page.goto(session_url)

            check_authorization(page)

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

            logging.info(f"Сессия {session_url} обработана")
            
        except:
            print(f"Ссессия {index} не обработана. Проверьте ссылку!")
            logging.error(f"Ошибка парсинга ссылки {session_url}")


    print("\nВсе сессии обработаны!")

    browser.close()