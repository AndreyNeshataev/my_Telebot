# from loguru import logger
# from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
#
#
# def inline_commands() -> InlineKeyboardMarkup:
#     """
#     Функция для создания инлайн - кнопок с командамаи бота
#     (Резерв, не задействована)
#     :return: keyboard: InlineKeyboardMarkup - клавиатура
#     """
#     try:
#         keyboard: InlineKeyboardMarkup = InlineKeyboardMarkup(row_width=1)
#         button_1: InlineKeyboardButton = InlineKeyboardButton('/lowprice', callback_data='/lowprice')
#         button_2: InlineKeyboardButton = InlineKeyboardButton('/highprice', callback_data='/highprice')
#         button_3: InlineKeyboardButton = InlineKeyboardButton('/bestdeal', callback_data='/bestdeal')
#
#         keyboard.add(button_1, button_2, button_3)
#         return keyboard
#
#     except Exception as exc:
#         logger.debug(exc)
#         logger.add('debug.log', format='{time} {level} {message}',
#                    level='DEBUG', rotation='1MB', compression='zip')

