from typing import Any
from loguru import logger
from telegram_bot_calendar import DetailedTelegramCalendar


def get_calendar(is_process: bool = False, callback_data: Any = None, **kwargs: Any) -> Any:
    """
    Функция для работы календаря
    :param is_process: bool
    :param callback_data:
    :param kwargs:
    :return:
    """
    try:
        if is_process:
            result, key, step = DetailedTelegramCalendar(calendar_id=kwargs['calendar_id'],
                                                         current_date=kwargs.get('current_date'),
                                                         min_date=kwargs['min_date'],
                                                         max_date=kwargs['max_date'],
                                                         locale=kwargs['locale']).process(callback_data.data)
            return result, key, step
        else:
            calendar, step = DetailedTelegramCalendar(calendar_id=kwargs['calendar_id'],
                                                      current_date=kwargs.get('current_date'),
                                                      min_date=kwargs['min_date'],
                                                      max_date=kwargs['max_date'],
                                                      locale=kwargs['locale']).build()
            return calendar, step
    except Exception as exc:
        logger.debug(exc)
        logger.add('debug.log', format='{time} {level} {message}',
                   level='DEBUG', rotation='1MB', compression='zip')


# словарь для русификации сообщений
ALL_STEPS: dict[str, str] = {'y': 'год', 'm': 'месяц', 'd': 'день'}
