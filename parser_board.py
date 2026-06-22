from func_to_parser import *
from playwright.sync_api import sync_playwright


with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()
    res_session = []  # Список для хранения ссылок(досок)

    #Цикл по ссылкам проектов
    for board in BOARDS:
        try:
            page.goto(board)
            page.wait_for_load_state("networkidle")

            check_authorization(page)  # Авторизация
            logging.info("Успешная аавторизация")

            page.wait_for_load_state("networkidle")
            logging.info("Успешная загрузка страницы с досками")


            # Ждём загрузки iframe(таблицы)
            page.wait_for_selector(".agilepoker-iframe")
            frame = page.frame_locator(".agilepoker-iframe")
            logging.info("Успешная загрузка iframe")
    
            # Ждём загрузку первой ссылки на доску
            frame.locator("tbody tr").first.wait_for()
            logging.info("Успешная первой ссылки на странице")


            rows_count = frame.locator("tbody tr").count()  # Переменная для подсчета кол-ва ссылок на странице
            logging.info(f"Ссылок на странице {rows_count}, ограничиваем до 10")
            rows_count = 5
            for i in range(rows_count):

                row = frame.locator("tbody tr").nth(i)
                status = row.locator(".aui-lozenge-current")

                # Проверка открыта сессия или нет
                if not status.is_visible():
                    continue
                if status.inner_text().strip() != "OPEN":
                    continue
    

                # Переходим по открытой сессии
                row.locator("a").first.click()
                page.wait_for_load_state("networkidle")
                logging.info("Успешная загрузка доски с оценками")

                
                res_session.append(page.url)  # Добаляем в список ссылок
                logging.info(f"Успешная добавление в res_session.\n{res_session}")
                print(f"OPEN сессия добавлена в список")
                break
                
                # Посчитал, что при первой найденной открытой сессии, мы выходим из цикла
                page.go_back()
                page.wait_for_load_state("networkidle")
                logging.info("Успешная загрузка после возврата на стрыницу с досками")
        
                # После возврата переинициализируем frame(Если первая сессия не подошла)
                page.wait_for_selector(".agilepoker-iframe")
                logging.info("Успешно 'page.wait_for_selector' ")
                frame = page.frame_locator(".agilepoker-iframe")
                logging.info("Успешно 'frame = page.frame_locator' ")
                frame.locator("tbody tr").first.wait_for()
                logging.info("Успешно 'frame.locator().first.wait_for()' ")
        except:
            print("Ошибка авторизации или парсинга страницы")
            logging.error(f"Ошибка авторизации или парсинга страницы {board}")


    browser.close()
