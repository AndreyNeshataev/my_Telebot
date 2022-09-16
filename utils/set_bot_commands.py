import requests
from loguru import logger
from telebot.types import BotCommand
from config_data.config import DEFAULT_COMMANDS


def set_default_commands(bot):
    """
    Функция для создания команд бота
    :param bot: Telebot
    """
    try:
        bot.set_my_commands([BotCommand(*i) for i in DEFAULT_COMMANDS])
    except requests.exceptions.ConnectTimeout as exc:
        logger.debug(exc)
        logger.add('debug.log', format='{time} {level} {message}',
                   level='DEBUG', rotation='1MB', compression='zip')
