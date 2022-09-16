from loguru import logger
from telebot.types import Message

from loader import bot


# Эхо хендлер, куда летит команда 'hello_world'
@bot.message_handler(commands=['hello_world'])
def hello_world(message: Message):
    try:
        sticker = open('C:\\Users\Андрей\Pictures\Saved Pictures\helloSticker.tgs', 'rb')
        bot.send_sticker(message.chat.id, sticker)
        bot.send_message(message.chat.id, f'Привет, {message.from_user.first_name}!', parse_mode='html')
    except Exception as exc:
        logger.debug(exc)
        # logger.exception(exc)
        logger.add('debug.log', format='{time} {level} {message}',
                   level='DEBUG', rotation='1MB', compression='zip')


@bot.message_handler(func=lambda msg: msg.text.lower() == 'привет')
def start_command(message: Message):
    try:
        bot.send_message(message.chat.id,
                         f'Привет, Привет\n'
                         f'Для взаимодействия с ботом выбери одну из команд в "МЕНЮ"',
                         parse_mode='html')
    except Exception as exc:
        logger.debug(exc)
        # logger.exception(exc)
        logger.add('debug.log', format='{time} {level} {message}',
                   level='DEBUG', rotation='1MB', compression='zip')
