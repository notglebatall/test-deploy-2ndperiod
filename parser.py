from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options





def parse_match_time(time_str):
    if time_str.strip().lower() == 'перерыв':
        return 0

    try:
        # Разделение строки на часть с периодом и часть с минутами
        period_info, minute_info = time_str.split(', ')

        # Извлечение информации о периоде
        period = int(period_info.split()[0])

        # Извлечение информации о минутах
        minutes = int(minute_info.split()[0])

        # Обычно в хоккее 1 период = 20 минут, поэтому общее количество минут:
        total_minutes = (period - 1) * 20 + minutes

        return total_minutes

    except (ValueError, IndexError):
        # Если строка не в ожидаемом формате, возвращаем 0
        return 0


def get_match_info(driver, url):
    driver.get(url)

    WebDriverWait(driver, 15)

    matches = driver.find_elements(By.CSS_SELECTOR,
                                   "div[class^='src-sportbook-common-components-MatchMiniCard-components-Card-__card--")
    match_list = []
    for match in matches:
        try:
            team_elements = match.find_elements(By.CSS_SELECTOR,
                                                "span[class^='src-sportbook-common-components-MatchMiniCard-components-Players-Player-__title--']")

            score_elements = match.find_elements(By.CSS_SELECTOR,
                                                 "span[class^='src-sportbook-common-components-MatchMiniCard-components-Score-__scoreValue--']")

            time = match.find_element(By.CSS_SELECTOR,
                                      "time[class^='src-sportbook-common-components-MatchMiniCard-components-MatchTime-__time--']")

            match_info = {
                "team_1": team_elements[0].text if len(team_elements) > 0 else "N/A",
                "team_2": team_elements[1].text if len(team_elements) > 1 else "N/A",
                "score_1": score_elements[2].text if len(score_elements) > 0 else "N/A",
                "score_2": score_elements[3].text if len(score_elements) > 1 else "N/A",
                "time": time.text if time else "N/A",
                "id": f'{team_elements[0].text} - {team_elements[1].text}' if len(team_elements) > 1 else "N/A",
                "url": ''
            }

            match_list.append(match_info)

        except Exception as e:
            print(f"Произошла ошибка при обработке матча: {e}")

    return match_list


with webdriver.Chrome() as chrome_driver:
    match_info = get_match_info(chrome_driver, url="https://betboom.ru/sport/live/basketball")
    for match in match_info:
        print(match)
