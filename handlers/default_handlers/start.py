from loguru import logger
from telebot.types import Message
from loader import bot
from states.state import SearchInfoState


@bot.message_handler(commands=['start'])
def start_command(message: Message):
    try:
        bot.send_message(message.chat.id,
                         f'Привет, {message.from_user.first_name}!\n'
                         f'Для взаимодействия с ботом выбери одну из команд в "МЕНЮ" в команде /help',
                         parse_mode='html')
    except Exception as exc:
        logger.debug(exc)
        logger.add('debug.log', format='{time} {level} {message}',
                   level='DEBUG', rotation='1MB', compression='zip')
