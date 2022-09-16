import requests
from loguru import logger
from telebot.types import Message, CallbackQuery

from database.data import set_user_data
from handlers.api import my_api
from loader import bot

logger.add('debug.log', format='{time} {level} {message}',
           level='DEBUG', rotation='1MB', compression='zip')


def info_user(user_id: int | str, chat_id: int | str) -> str:
    """
    Функция для формирования текста, введенной пользователем информации
    :param user_id: Any
    :param chat_id: Any
    :return: text: str
    """
    try:
        with bot.retrieve_data(user_id, chat_id) as data:
            text: str = f'Спасибо за предоставленную информацию:\n' \
                        f'Имя: {data["name"]}\n' \
                        f'Город: {data["city"]}\n' \
                        f'Локация в городе {data["destination"]}\n' \
                        f'Дата заезда: {data["check_in"]}\n' \
                        f'Дата выезда: {data["check_out"]}\n' \
                        f'Количество дней отдыха: {data["number_day"]}\n'
            if 'price_min' in data.keys():
                text += f'Минимальная цена: {data["price_min"]}\n'
            if 'price_max' in data.keys():
                text += f'Максимальная цена: {data["price_max"]}\n'
            if 'distance_range' in data.keys():
                text += f'Расстояние от центра города: {data["distance_range"]}\n'
            if 'number_hotels' in data.keys():
                text += f'Количество отелей: {data["number_hotels"]}\n'
            if 'number_photos' in data.keys():
                text += f'Количество фотографий: {data["number_photos"]}\n'
            text += f'Вы выбрали команду: {data["command"]}\n'

            return text
    except requests.exceptions.ConnectTimeout as exc:
        logger.debug(exc)


def get_info_hotel(message: Message | CallbackQuery, is_rejection: bool = False) -> None:
    """
    Функция вывода информации по отелям и
    запуска функции поиска и вывода фотографий
    :param message: Message | CallbackQuery
    :param is_rejection: bool
    """
    try:
        if is_rejection:
            user_id: int | str = message.from_user.id
            chat_id: int | str = message.message.chat.id
        else:
            user_id: int | str = message.from_user.id
            chat_id: int | str = message.chat.id
        bot.send_message(chat_id=user_id,
                         text=f'Отлично! Опрос окончен!\n'
                              f'{info_user(user_id, chat_id)}\n\n'
                              f'Подожди немного. Веду поиск...',
                         parse_mode='html')

        with bot.retrieve_data(user_id, chat_id) as data:
            hotels: list = data['hotels_info']
            if len(hotels) == 0:
                bot.send_message(chat_id=user_id,
                                 text='К сожалению, по вашему запросу ничего не найдено',
                                 parse_mode='html')
            else:
                if len(hotels) > int(data['number_hotels']):
                    hotels = hotels[:int(data['number_hotels'])]
                elif len(hotels) < int(data['number_hotels']):
                    bot.send_message(chat_id=user_id,
                                     text=f'К сожалению, по указанным ценовому диапазону и расстоянию'
                                          f' от центра я не нашел {data["number_hotels"]} отелей,'
                                          f' покажу только {len(hotels)}',
                                     parse_mode='html')
                for hotel in hotels:
                    hotel_info: str = f'Название отеля: {hotel["hotel_name"]}\n' \
                                      f'Адрес отеля: {hotel["address"]}\n' \
                                      f'Звездный рейтинг: {hotel["starRating"]}\n' \
                                      f'Рейтинг отеля: {hotel["rating"][0]} из {hotel["rating"][1]}\n' \
                                      f'Расстояние от {hotel["landmarks_1"][0]} до отеля: {hotel["landmarks_1"][1]}\n'
                    if hotel["landmarks_2"] is not None:
                        hotel_info += f'Расстояние от {hotel["landmarks_2"][0]} до отеля: {hotel["landmarks_2"][1]}\n'
                    hotel_info += f'Стоимость проживания за 1 день: {hotel["price_1"]} руб\n' \
                                  f'Стоимость проживания за {data["number_day"]} дней: {hotel["price_2"]} руб\n' \
                                  f'Ссылка на сайт: https://www.hotels.com/ho{hotel["hotel_id"]}'
                    if data['number_photos'] == 'Не требуется':
                        bot.send_message(chat_id=user_id,
                                         text=hotel_info,
                                         parse_mode='html')
                    elif int(data['number_photos']) > 0:
                        media: list = my_api.photo_founding(number_photos=data['number_photos'],
                                                            info=hotel_info,
                                                            hotel_id=hotel['hotel_id'],
                                                            user_id=user_id,
                                                            )
                        bot.send_media_group(chat_id=chat_id, media=media)

                    set_user_data(name=data['name'],
                                  telegram_id=user_id,
                                  city=data['city'],
                                  check_in=data['check_in'],
                                  check_out=data['check_out'],
                                  hotel=hotel["hotel_name"],
                                  link=f'https://www.hotels.com/ho{hotel["hotel_id"]}')

    except requests.exceptions.ConnectTimeout as exc:
        logger.debug(exc)
