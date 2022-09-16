import os
from dotenv import load_dotenv, find_dotenv

if not find_dotenv():
    exit('Переменные окружения не загружены т.к отсутствует файл .env')
else:
    load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')
RAPID_API_KEY = os.getenv('RAPID_API_KEY')

headers = {
    "X-RapidAPI-Key": RAPID_API_KEY,
    "X-RapidAPI-Host": "hotels4.p.rapidapi.com"
}

DEFAULT_COMMANDS = (
    ('start', 'Запустить бота'),
    ('help', 'Помощь по командам бота'),  # ,('hello_world', 'возвращает приветствие')
    ('reset', 'Завершение сессии')
)

MAX_NUM_HOTELS = 5
MAX_NUM_PHOTOS = 10
