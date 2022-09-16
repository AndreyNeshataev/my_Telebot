from loguru import logger
from telebot import TeleBot
from config_data import config

# Создаем бота

try:
    bot: TeleBot = TeleBot(token=config.BOT_TOKEN)
except Exception as exc:
    logger.debug(exc)
    logger.add('debug.log', format='{time} {level} {message}',
               level='DEBUG', rotation='1MB', compression='zip')
