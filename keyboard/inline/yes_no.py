from loguru import logger
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton


def yes_no() -> InlineKeyboardMarkup:
    """
    Функция для создания инлайн - кнопок с ДА, НЕТ
    :return: keyboard: InlineKeyboardMarkup - клавиатура
    """
    try:
        keyboard: InlineKeyboardMarkup = InlineKeyboardMarkup(row_width=2)
        button_1: InlineKeyboardButton = InlineKeyboardButton('ДА', callback_data='yes')
        button_2: InlineKeyboardButton = InlineKeyboardButton('НЕТ', callback_data='no')

        keyboard.add(button_1, button_2)
        return keyboard

    except Exception as exc:
        logger.debug(exc)
        logger.add('debug.log', format='{time} {level} {message}',
                   level='DEBUG', rotation='1MB', compression='zip')
