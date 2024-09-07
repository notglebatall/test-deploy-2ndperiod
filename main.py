import logging
import schedule
import asyncio

from telegram import Bot
from selenium import webdriver
from parser import get_values, get_team_names

# URL целевой страницы с матчами
URL = 'https://www.sofascore.com/api/v1/sport/ice-hockey/events/live'
TELEGRAM_TOKEN = '7247970905:AAFusLnzp6XpCDX5txtmUKZBdzRSqku5GyA'
CHAT_ID = -4564242872

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Множество для хранения идентификаторов событий, о которых уже было уведомление
notified_events = set()


async def check_conditions_and_notify(match_list, bot):
    for match in match_list:
        # Уникальный идентификатор события используется, чтобы избежать повторных уведомлений
        if match['name'] not in notified_events:
            logging.info(f"Проверка условия для события {match['name']}")

            # Основное условие по времени матча
            if int(match['time'].split(':')[0]) >= 30:
                # Формируем отдельные части сообщения в зависимости от условий
                team_1_odds = ""
                team_2_odds = ""

                # Проверка для первой команды
                if int(match['score_1']) == 0 and float(match['value_more_1']) > 1.5:
                    team_1_odds = (f"Коэффициент на {match['team_1']} {match['total_text_1']}:\n\n"
                                   f"Больше: {match['value_more_1']}\n"
                                   f"Меньше: {match['value_less_1']}\n\n")

                # Проверка для второй команды
                if int(match['score_2']) == 0 and float(match['value_more_2']) > 1.5:
                    team_2_odds = (f"Коэффициент на {match['team_2']} {match['total_text_2']}:\n\n"
                                   f"Больше: {match['value_more_2']}\n"
                                   f"Меньше: {match['value_less_2']}\n\n")

                # Если хотя бы одно из дополнительных условий выполнено, формируем сообщение
                message = ""  # Инициализация переменной message
                if team_1_odds or team_2_odds:
                    message = (f"Матч: {match['team_1']} - {match['team_2']}\n\n"
                               f"Счет: {match['score_1']} - {match['score_2']}\n"
                               f"Время игры: {match['time']}\n\n"
                               f"{team_1_odds}"
                               f"{team_2_odds}"
                               f"Ссылка на событие: {match['link']}")

                if message:  # Отправляем сообщение только если оно не пустое
                    logging.info(f"Отправка уведомления для события {match['name']}")
                    await bot.send_message(chat_id=CHAT_ID, text=message)
                    notified_events.add(match['name'])  # Добавление события в множество уведомленных
                else:
                    logging.info(f"Событие {match['name']} не проходит дополнительные проверки")
            else:
                logging.info(f"Событие {match['name']} не подходит по времени")


async def job():
    logging.info("Запуск парсера...")
    bot = Bot(token=TELEGRAM_TOKEN)
    chrome_driver = None

    try:
        chrome_driver = webdriver.Chrome()
        match_list = get_team_names(chrome_driver, url="https://fon.bet/live/hockey")
        values_list = get_values(chrome_driver, match_list)

        if values_list:
            logging.info(f"Найдено {len(values_list)} событий для проверки.")
            await check_conditions_and_notify(values_list, bot)
        else:
            logging.info('Новых событий нет')

    except Exception as e:
        logging.error(f"Ошибка в процессе работы job: {e}")

    finally:
        if chrome_driver:
            chrome_driver.quit()
            logging.info("ChromeDriver закрыт")


async def main():
    await asyncio.create_task(job())
    # Запуск задачи каждые 3 минуты
    schedule.every(3).minutes.do(lambda: asyncio.create_task(job()))

    while True:
        schedule.run_pending()
        await asyncio.sleep(1)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info('Бот выключен')
