from loguru import logger
from telebot.types import Message

from handlers.custom_handlers import survey
from loader import bot


# Эхо хендлер, куда летят текстовые сообщения без указанного состояния
@bot.message_handler(content_types=['text'])
def bot_echo(message: Message):
    try:
        if message.text not in ['/lowprice', '/highprice', '/bestdeal', '/history']:
            bot.send_message(message.chat.id,
                             'Я тебя не понимаю. Введи одну из объявленных команд\n'
                             '/lowprice — вывод самых дешёвых отелей в городе\n'
                             '/highprice — вывод самых дорогих отелей в городе\n'
                             '/bestdeal — вывод отелей, наиболее подходящих по цене и расположению от центра\n '
                             '/history — вывод истории поиска отелей\n'
                             'Сделайте выбор и нажмите одну из команд',
                             parse_mode='html')
        else:
            survey.command(message)
    except Exception as exc:
        logger.debug(exc)
        # logger.exception(exc)
        logger.add('debug.log', format='{time} {level} {message}',
                   level='DEBUG', rotation='1MB', compression='zip')
