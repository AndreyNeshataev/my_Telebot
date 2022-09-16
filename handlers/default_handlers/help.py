from loguru import logger
from telebot.types import Message

from loader import bot


# Это хендлер, куда летит команда 'help'
@bot.message_handler(commands=['help'])
def help_command(message: Message):
    try:
        text = 'В данном боте можно выбрать отель в интересующем городе по' \
               'следующим параметрам:\n' \
               '/lowprice — вывод самых дешёвых отелей в городе\n' \
               '/highprice — вывод самых дорогих отелей в городе\n' \
               '/bestdeal — вывод отелей, наиболее подходящих по цене и расположению от центра\n' \
               '/history — вывод истории поиска отелей\n' \
               'Сделайте выбор и нажмите одну из команд'
        bot.send_message(message.chat.id, text, parse_mode='html')
    except Exception as exc:
        logger.debug(exc)
        # logger.exception(exc)
        logger.add('debug.log', format='{time} {level} {message}',
                   level='DEBUG', rotation='1MB', compression='zip')
