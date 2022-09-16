from loguru import logger
from telebot.types import Message
from states.state import SearchInfoState
from loader import bot


# Эхо хендлер, куда летит команда 'reset'
@bot.message_handler(state=SearchInfoState)
@bot.message_handler(commands=['reset'])
def exit_command(message: Message):
    try:
        bot.send_message(message.chat.id, 'Заканчиваем эту сессию',
                         parse_mode='html')
        bot.send_message(message.chat.id, 'Для возобновления нажми на команду:\n'
                                          '/start',
                         parse_mode='html')
        bot.set_state(message.from_user.id, SearchInfoState.command, message.chat.id)
    except Exception as exc:
        logger.debug(exc)
        # logger.exception(exc)
        logger.add('debug.log', format='{time} {level} {message}',
                   level='DEBUG', rotation='1MB', compression='zip')
