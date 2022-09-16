from loguru import logger
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, Message, ReplyKeyboardRemove
from handlers.api import my_api

city_id: dict = dict()


def city_markup(message: Message) -> InlineKeyboardMarkup | None:
    """
    Функция создает кнопки с локациями в городе и
    возвращает список словарей с нужным именем и id
    :param message: Message
    :return: destinations: InlineKeyboardMarkup - клавиатура
    """
    try:
        cities: list[dict[str, str]] = my_api.city_founding(message)
        destinations: InlineKeyboardMarkup = InlineKeyboardMarkup()
        if cities:
            for city in cities:
                destinations.add(InlineKeyboardButton(text=city['city_name'],
                                                      callback_data=city["destination_id"]))
                city_id[city["destination_id"]] = city['city_name']
            return destinations
    except Exception as exc:
        logger.debug(exc)
        logger.add('debug.log', format='{time} {level} {message}',
                   level='DEBUG', rotation='1MB', compression='zip')
