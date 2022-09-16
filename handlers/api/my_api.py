from typing import List, Dict, Match, Any
import re
import json
from requests import Response
from telebot.types import Message, InputMediaPhoto
from loguru import logger
from config_data.config import headers
from handlers.api.request import request_to_api
from loader import bot
from states.state import SearchInfoState

# logger.remove(handler_id=None)
logger.add('debug.log', format='{time} {level} {message}',
           level='DEBUG', rotation='1MB', compression='zip')


def city_founding(message: Message) -> List[Dict[str, str]]:
    """
    Функция формирования списка локаций в городе
    :param message: Message - сообщение с названием города
    :return: cities : List[dict] - список словарей с информацией о локациях
    """
    try:
        city_url: str = 'https://hotels4.p.rapidapi.com/locations/v2/search'
        querystring: dict[str, str] = {'query': message.text, 'locale': 'ru_RU', 'currency': 'RUB'}
        response: Response = request_to_api(url=city_url, headers=headers, querystring=querystring)

        pattern: str = r'(?<="CITY_GROUP",).+?[\]]'
        find: Match[str] = re.search(pattern, response.text)

        suggestions = None
        if find:
            suggestions = json.loads(f"{{{find[0]}}}")

        cities: list[dict[str, str]] = list()
        for dest_id in suggestions['entities']:
            pattern: str = r'<.+?>'
            clear_destination: str = re.sub(pattern, '', dest_id['caption'])
            cities.append({'city_name': clear_destination, 'destination_id': dest_id['destinationId']})
            with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
                if data['command'] == '/bestdeal':
                    break
        return cities
    except Exception as exc:
        logger.debug(exc)


def hotel_founding(user_id: Any, chat_id: Any) -> None:
    """
    Функция формирования списка отелей в городе
    и определения минимальной цены по выбранным отелям
    :param chat_id: Any - ID чата
    :param user_id: Any - ID пользователя
    """
    hotels_info = list()

    landmarkIds: str = ''
    hotels_url: str = "https://hotels4.p.rapidapi.com/properties/list"

    with bot.retrieve_data(user_id, chat_id) as data:
        number_day = data['number_day']
        if data['command'] == '/lowprice':
            sortOrder = 'PRICE'
        elif data['command'] == '/highprice':
            sortOrder = 'PRICE_HIGHEST_FIRST'
        elif data['command'] == '/bestdeal':
            sortOrder = 'DISTANCE_FROM_LANDMARK'
            landmarkIds = 'Центр города'
        querystring: dict[str, str] = {'destinationId': data['destinationID'], 'pageNumber': '1', 'pageSize': '25',
                                       'checkIn': data['check_in'], 'checkOut': data['check_out'], 'adults1': '1',
                                       'sortOrder': sortOrder, 'locale': 'ru_RU', 'currency': 'RUB',
                                       'landmarkIds': landmarkIds}
        response: bool | Response = request_to_api(url=hotels_url, headers=headers, querystring=querystring)
    try:
        pattern: str = r'(?<=,)"results":.+?(?=,"pagination)'
        find: Match[str] = re.search(pattern, response.text)

        suggestions = None
        if find:
            suggestions = json.loads(f"{{{find[0]}}}")

        for hotel in suggestions['results']:
            try:
                hotel_id: str = hotel['id']
                hotel_name: str = hotel['name']
                address: str = hotel['address']['streetAddress']
                starRating: str = hotel['starRating']
                rating: list[str] = [hotel['guestReviews']['rating'], hotel['guestReviews']['scale']]
                landmarks_1: list[str] = [hotel['landmarks'][0]['label'], hotel['landmarks'][0]['distance']]
                if len(hotel['landmarks']) > 1:
                    landmarks_2 = [hotel['landmarks'][1]['label'], hotel['landmarks'][1]['distance']]
                else:
                    landmarks_2 = None
                price_1: str = hotel['ratePlan']['price']['exactCurrent']
                price_2: str = str(int(hotel['ratePlan']['price']['exactCurrent']) * int(number_day))
                hotels_info.append({'hotel_id': hotel_id, 'hotel_name': hotel_name, 'address': address,
                                    'starRating': starRating, 'rating': rating, 'landmarks_1': landmarks_1,
                                    'landmarks_2': landmarks_2, 'price_1': price_1, 'price_2': price_2})
            except (LookupError, ValueError) as exc:
                logger.debug(exc)

        min_price: str = (min(hotels_info, key=lambda x: x['price_1']))['price_1']
        data['min_price_real'] = min_price
        data['hotels_info'] = hotels_info
    except Exception as exc:
        logger.debug(exc)


def get_distance_best(message: Message) -> None:
    """
    Функция для создания списка отелей по заданному диапазону цен и
    определения минимального расстояния из списка отелей от центра,
    по заданному диапазону цен
    :param message: Message
    """
    try:
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            hotels_info = data['hotels_info']
            MAX: str = data['price_max']
            MIN: str = data['price_min']
            hotels_info: list = list(
                filter(lambda x: (int(MIN) <= float(x['price_1']) <= int(MAX)), hotels_info))
            if len(hotels_info) > 0:
                min_distans_dict: Any = min(hotels_info, key=lambda x: x['landmarks_1'][1])
                min_distance_real: Any = min_distans_dict['landmarks_1'][1][:-3].replace(',', '.')
                data['min_distance_real'] = min_distance_real
                data['hotels_info'] = hotels_info
                if message.text.isdigit() and \
                        int(message.text) > float(data['price_min']) and \
                        int(message.text) > float(data['min_price_real']):
                    bot.set_state(message.from_user.id,
                                  SearchInfoState.distance_range,
                                  message.chat.id)
                    bot.send_message(chat_id=message.from_user.id,
                                     text=f'Ок, записал!\nВведи расстояние от центра города (км).\n'
                                          f'Фактическое минимальное расстояние'
                                          f' от центра до отеля в выбранной локации'
                                          f' в заданном ценовом диапазоне составляет '
                                          f'{data["min_distance_real"]} км',
                                     parse_mode='html')
            else:
                bot.set_state(message.from_user.id,
                              SearchInfoState.price_min,
                              message.chat.id)
                bot.send_message(chat_id=message.from_user.id,
                                 text=f'К сожалению в указанном ценовом диапазоне отели не найдены.\n'
                                      f'Измените диапазон цен. Попробуйте снизить минимальную цену и '
                                      f'увеличить максимальную.\n\n'
                                      f'Сначала введите минимальную цену за одни сутки.\n'
                                      f'Фактическая минимальная цена за один день в выбранной локации '
                                      f'{data["min_price_real"]} руб.\n'
                                      f'Либо перезапустите сессию командой /reset',
                                 parse_mode='html')
    except Exception as exc:
        logger.debug(exc)


def get_hotels_best(hotels_info: list, distance: str) -> list:
    """
    Функция для создания списка отелей по заданному диапазону цен
    и по заданному расстоянию от центра города
    :param hotels_info: : list - список с информацией по отелям
    :param distance: str - расстояние от центра города до отеля, введенное пользователем
    """
    try:
        distance: str = distance.replace(',.', '.')
        hotels_info: list = \
            list(
                filter(lambda x: float(x['landmarks_1'][1][:-3].replace(',', '.')) <= float(distance),
                       hotels_info))
        hotels_info.sort(key=lambda x: x['price_1'])
        return hotels_info
    except Exception as exc:
        logger.debug(exc)


def photo_founding(**kwargs: int | str):
    """
    Функция формирования списка ссылок фотографий отелей
    и вывода в телебот фотографий
    param: **kwargs: int | str
    :return: list - список ссылок фотографий отелей
    """
    number_photos = kwargs['number_photos']
    info = kwargs['info']
    hotel_id = kwargs['hotel_id']
    user_id = kwargs['user_id']
    photos_url: str = 'https://hotels4.p.rapidapi.com/properties/get-hotel-photos'
    querystring: dict = {'id': hotel_id}

    response: Response = request_to_api(url=photos_url, headers=headers, querystring=querystring)
    photos: list[str] = list()

    try:
        suggestions = json.loads(response.text)
        media: list[InputMediaPhoto] = []
        for photo in suggestions['hotelImages']:
            url_photo: str = photo['baseUrl'].replace('{size}', 'w')
            photos.append(url_photo)

        if len(photos) > int(number_photos):
            photos: list[str] = photos[:int(number_photos)]
        if len(photos) == 0:
            bot.send_message(chat_id=user_id,
                             text=f'К сожалению, я не нашел ни одной фотографии, '
                                  f'покажу только информацию по отелям\n'
                                  f'{info}',
                             parse_mode='html')
        elif len(photos) > 0:
            media: list[InputMediaPhoto] = ([InputMediaPhoto(link, caption=info) if photos.index(link) == 0
                                             else InputMediaPhoto(link)
                                             for link in photos])
            if len(photos) < int(number_photos):
                bot.send_message(chat_id=user_id,
                                 text=f'К сожалению, я не нашел {number_photos} фотографий,'
                                      f'покажу только {len(photos)}',
                                 parse_mode='html')
        return media
    except Exception as exc:
        logger.debug(exc)
