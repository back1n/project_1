import re
from read_to_config import *
from func_to_parser import *
from playwright.sync_api import sync_playwright


with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    res_session = []  # Список для хранения ссылок(досок)

    #Цикл по ссылкам проектов
    for board in BOARDS:
        try:
            page.goto(board)
            page.wait_for_load_state("networkidle")
            
            check_authorization(page)  # Авторизация

            page.wait_for_load_state("networkidle")

            # Ждём загрузки iframe(таблицы)
            page.wait_for_selector(".agilepoker-iframe")
            frame = page.frame_locator(".agilepoker-iframe")
    
            # Ждём загрузку первой ссылки на доску
            frame.locator("tbody tr").first.wait_for()


            rows_count = frame.locator("tbody tr").count()  # Переменная для подсчета кол-ва ссылок на странице
            for i in range(rows_count):
                row = frame.locator("tbody tr").nth(i)
                status = row.locator(".aui-lozenge-current")

                # Проверка открыта сессия или нет
                if not status.is_visible():
                    continue
                if status.inner_text().strip() != "OPEN":
                    continue
                    
                print(f"OPEN сессия найдена ")
                # Переходим по открытой сессии
                row.locator("a").first.click()
                page.wait_for_load_state("networkidle")

                
                res_session.append(page.url)  # Добаляем в список ссылок
        
                page.go_back()
                page.wait_for_load_state("networkidle")
        
                # После возврата переинициализируем frame(Если первая сессия не подошла)
                page.wait_for_selector(".agilepoker-iframe")
                frame = page.frame_locator(".agilepoker-iframe")
                frame.locator("tbody tr").first.wait_for()
        except:
            print("Ошибка авторизации или парсинга страницы")
            logging.error(f"Ошибка авторизации или парсинга страницы {board}")


        # Цикл по Доскам
        for index, session_url in enumerate(res_session, start=1):
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
                
                print("\nСессия обработана")
                logging.info(f"Сессия {session_url} обработана")
            except:
                print(f"Ссессия {index} не обработана. Проверьте ссылку!")
                logging.error(f"Ошибка парсинга ссылки {session_url}")
            else:
                print("\nВсе сессии обработаны!")
                logging.info("Все сессии обработаны")

    
    browser.close()