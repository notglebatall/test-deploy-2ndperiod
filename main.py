import requests
import logging
import schedule
import asyncio
from telegram import Bot

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


def format_time(played_time):
    # Каждый период длится 20 минут = 1200 секунд
    seconds_per_period = 1200

    period = (played_time // seconds_per_period) + 1  # Определение текущего периода
    remaining_seconds = played_time % seconds_per_period  # Секунды в текущем периоде

    minutes = remaining_seconds // 60  # Минуты в текущем периоде
    seconds = remaining_seconds % 60  # Оставшиеся секунды

    return f"{period} - {minutes} - {seconds}"


# Множество для хранения идентификаторов событий, о которых уже было уведомление
notified_events = set()

def parse_events():
    try:
        response = requests.get(URL)
        data = response.json()
        events = [x for x in data['events']]
        result = []
        for event in events:
            if all(k in event for k in ('id', 'homeTeam', 'homeScore', 'awayTeam', 'awayScore', 'time')) and 'played' in \
                    event['time']:
                result.append({
                    'id': event['id'],
                    'home_team': event['homeTeam']['name'],
                    'home_score': event['homeScore']['current'],
                    'away_team': event['awayTeam']['name'],
                    'away_score': event['awayScore']['current'],
                    'played_time': event['time']['played']
                })
        return result
    except Exception as e:
        logging.error(f"Ошибка при парсинге событий: {e}")
        return []

async def check_conditions_and_notify(events, bot):
    for event in events:
        # Уникальный идентификатор события используется, чтобы избежать повторных уведомлений
        if event['id'] not in notified_events:
            logging.info(f"Проверка условия для события {event['id']}")
            if event['played_time'] > 1800 and (event['home_score'] == 0 or event['away_score'] == 0):
                message = (f"Матч: {event['home_team']} vs {event['away_team']}\n\n"
                           f"Счет: {event['home_score']} - {event['away_score']}\n"
                           f"Время игры: {int(format_time(event['played_time']))} секунд\n"
                           "Один из счетов равен 0!")
                logging.info(f"Отправка уведомления для события {event['id']}")
                await bot.send_message(chat_id=CHAT_ID, text=message)
                notified_events.add(event['id'])  # Добавление события в множество уведомленных

async def job():
    logging.info("Запуск парсера...")
    events = parse_events()
    bot = Bot(token=TELEGRAM_TOKEN)
    if events:
        logging.info(f"Найдено {len(events)} событий для проверки.")
        await check_conditions_and_notify(events, bot)
    else:
        logging.info('Новых событий нет')
async def main():
    # Запуск задачи каждые 5 минут
    asyncio.create_task(job())

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


