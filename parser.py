import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def get_team_names(driver, url="https://fon.bet/live/hockey"):
    driver.get(url)


    css_selector = "a.table-component-text--Tjj3g.sport-event__name--YAs00._clickable--xICGO._event-view--nrsM2._compact--MZ0VP[data-testid='event']"

    WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, css_selector)))
    matches = driver.find_elements(By.CSS_SELECTOR, css_selector)

    match_list = [{
        'name': match.text,
        'link': match.get_attribute('href')
    } for match in matches]

    print(f'Найдено матчей: {len(match_list)}')

    return match_list


def get_values(driver, matches):
    values_data = []

    original_window = driver.current_window_handle

    for match in matches:
        # Открываем новую вкладку
        driver.execute_script("window.open('');")

        # Переключаемся на новую вкладку
        driver.switch_to.window(driver.window_handles[-1])
        driver.get(match['link'])

        try:
            WebDriverWait(driver, 10).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, 'span.scoreboard-timer__value--lpnFb'))
            )
            match_time = driver.find_element(By.CSS_SELECTOR, 'span.scoreboard-timer__value--lpnFb').text


            WebDriverWait(driver, 10).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, 'div.column__t1--WCEcc'))
            )
            column_values_1 = driver.find_elements(By.CSS_SELECTOR, 'div.column__t1--WCEcc')
            column_values_2 = driver.find_elements(By.CSS_SELECTOR, 'div.column__t2--rn4_E')

            team_name_1 = column_values_1[0].text
            team_name_2 = column_values_2[0].text

            score_1 = column_values_1[1].text
            score_2 = column_values_2[1].text

            WebDriverWait(driver, 10).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, 'div.tables--nx9N8'))
            )
            table = driver.find_element(By.CSS_SELECTOR, 'div.tables--nx9N8')

            WebDriverWait(driver, 10).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, 'div.group--sb27t'))
            )
            groups = table.find_elements(By.CSS_SELECTOR, "div.group--sb27t")


            WebDriverWait(driver, 10).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, 'div.market-group-box--fCog3'))
            )
            boxes = groups[-1].find_elements(By.CSS_SELECTOR, "div.market-group-box--fCog3")


            WebDriverWait(driver, 10).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, 'div.section--OIDNE._horizontal--rd1ss'))
            )
            sections = boxes[0].find_elements(By.CSS_SELECTOR, 'div.section--OIDNE._horizontal--rd1ss')


            WebDriverWait(driver, 10).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, 'div.normal-row--qsziU'))
            )
            rows = sections[0].find_elements(By.CSS_SELECTOR, 'div.normal-row--qsziU')


            rows_2 = sections[1].find_elements(By.CSS_SELECTOR, 'div.normal-row--qsziU')



            # Прокручиваем страницу к первому ряду
            driver.execute_script("arguments[0].scrollIntoView(true);", rows[0])


            time.sleep(3)

            cells = rows[0].find_elements(By.CSS_SELECTOR, 'div.cell--NEHKQ')


            total_text_1 = cells[0].text

            value_more_1 = cells[1].find_elements(By.CSS_SELECTOR, 'div.value--v77pD')
            value_less_1 = cells[2].find_elements(By.CSS_SELECTOR, 'div.value--v77pD')

            cells_2 = rows_2[0].find_elements(By.CSS_SELECTOR, 'div.cell--NEHKQ')


            total_text_2 = cells_2[0].text

            value_more_2 = cells_2[1].find_elements(By.CSS_SELECTOR, 'div.value--v77pD')
            value_less_2 = cells_2[2].find_elements(By.CSS_SELECTOR, 'div.value--v77pD')

            match_info = {
                'name': match['name'],
                'link': match['link'],
                'team_1': team_name_1,
                'team_2': team_name_2,
                'score_1': score_1,
                'score_2': score_2,
                'time': match_time,
                'total_text_1': total_text_1,
                'value_more_1': value_more_1[0].text if value_more_1 else None,
                'value_less_1': value_less_1[0].text if value_less_1 else None,
                'total_text_2': total_text_2,
                'value_more_2': value_more_2[0].text if value_more_2 else None,
                'value_less_2': value_less_2[0].text if value_more_2 else None

            }

            print(f'Собрана информация по матчу: {match_info}\n')

            values_data.append(match_info)

        except Exception as e:
            print(f"Ошибка при обработке матча {match['name']}: {str(e)}")

        # Закрываем текущую вкладку и возвращаемся на оригинальную
        driver.close()
        driver.switch_to.window(original_window)

    return values_data


