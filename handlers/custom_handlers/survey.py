import requests
from datetime import date, timedelta
from loguru import logger
from telegram_bot_calendar import DetailedTelegramCalendar
from config_data.config import MAX_NUM_HOTELS, MAX_NUM_PHOTOS
from database.data import get_info_data
from keyboard.inline import cities
from keyboard.inline.calendar import get_calendar, ALL_STEPS
from keyboard.inline.cities import city_id
from keyboard.inline.yes_no import yes_no
from loader import bot
from states.state import SearchInfoState
from telebot.types import Message, CallbackQuery
from handlers.api import my_api
from utils.info import get_info_hotel

logger.add('debug.log', format='{time} {level} {message}',
           level='DEBUG', rotation='1MB', compression='zip')


@bot.message_handler(commands=['history'])
def history(message: Message) -> None:
    """
    Функция, которая создает базу данных по запросам пользователей
    :param message: Message
    :return:
    """
    try:
        with bot.retrieve_data(user_id=message.from_user.id,
                               chat_id=message.chat.id) as data:
            query = get_info_data(user_id=message.from_user.id,
                                  name=data['name'])
            bot.send_message(chat_id=message.from_user.id,
                             text=f'Хорошо {data["name"]}, покажу последние, но не больше 10 отелей',
                             parse_mode='html')
            for info_hotel in query:
                bot.send_message(chat_id=message.from_user.id,
                                 text=f'Дата запроса: {info_hotel.date.strftime("%m-%d-%Y %H:%M:%S")}\n'
                                      f'Город поиска: {info_hotel.city}\n'
                                      f'Период проживания в отеле: c {info_hotel.check_in} по {info_hotel.check_out}\n'
                                      f'Название отеля: {info_hotel.hotel}\n'
                                      f'Ссылка на сайт: {info_hotel.link}\n',
                                 parse_mode='html')
    except LookupError as exc:
        logger.debug(exc)
        bot.send_message(chat_id=message.from_user.id,
                         text='К сожалению, история поиска пока пуста',
                         parse_mode='html')


@bot.message_handler(commands=['lowprice', 'highprice', 'bestdeal'])
def command(message: Message) -> None:
    """
    Функция, принимающая одну из команд 'lowprice', 'highprice', 'bestdeal',
    сохраняет команду
    и задает вопрос о имени пользователя и запускает первое состояние "name"
    :param message: Message
    """
    try:
        bot.delete_state(user_id=message.from_user.id,
                         chat_id=message.chat.id)
        bot.set_state(user_id=message.from_user.id,
                      state=SearchInfoState.name,
                      chat_id=message.chat.id)
        bot.send_message(message.from_user.id,
                         'Введи свое имя',
                         parse_mode='html')
        with bot.retrieve_data(user_id=message.from_user.id,
                               chat_id=message.chat.id) as data:  # Exception
            data['command'] = message.text
    except requests.exceptions.ConnectTimeout as exc:
        logger.debug(exc)


@bot.message_handler(state=SearchInfoState.name)
def name(message: Message) -> None:
    """
    Функция, принимающая состояние "name",
    сохраняет имя пользователя
    и задает вопрос о городе в котором будет происходить поиск отеля
    :param message: Message
    """
    try:
        if message.text.isalpha():
            bot.send_message(chat_id=message.from_user.id,
                             text='Спасибо, записал, введи город в котором будем искать отель',
                             parse_mode='html')

            with bot.retrieve_data(user_id=message.from_user.id,
                                   chat_id=message.chat.id) as data:
                data['name'] = message.text.capitalize()
            bot.set_state(user_id=message.from_user.id,
                          state=SearchInfoState.city,
                          chat_id=message.chat.id)
        else:
            bot.send_message(chat_id=message.from_user.id,
                             text='Имя должно состоять только из букв',
                             parse_mode='html')
    except requests.exceptions.ConnectTimeout as exc:
        logger.debug(exc)


@bot.message_handler(state=SearchInfoState.city)
def city(message: Message) -> None:
    """
    Функция для запроса локации и вывода инлайн кнопок с локациями
    :param message: Message
    """
    try:
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['city'] = message.text.capitalize()

        markup = cities.city_markup(message)
        if markup is not None:
            bot.send_message(chat_id=message.from_user.id,
                             text='Локация',
                             reply_markup=markup)  # Отправляем кнопки с вариантами
        else:
            bot.send_message(chat_id=message.from_user.id,
                             text='K сожалению данного города нет в нашей базе, '
                                  'попробуйте выбрать другой. Введите название города',
                             parse_mode='html')
    except requests.exceptions.ConnectTimeout as exc:
        logger.debug(exc)


@bot.callback_query_handler(func=lambda call: call.data.isdigit())
def callback_destination(call: CallbackQuery) -> None:
    """
    Функция, которая ловит id локации в городе и сохраняет
    и сохраняет ее,
    создается и отправляется календарь
    :param call: CallbackQuery
    """
    try:
        bot.edit_message_text(text='Спасибо, записал',
                              chat_id=call.message.chat.id,
                              message_id=call.message.message_id,
                              parse_mode='html',
                              reply_markup=None)

        with bot.retrieve_data(user_id=call.from_user.id,
                               chat_id=call.message.chat.id) as data:
            data['destinationID'] = call.data
            data['destination'] = city_id[call.data]

        # Отправляем календарь
        today: date = date.today()
        calendar, step = get_calendar(calendar_id=1,
                                      current_date=today,
                                      min_date=today,
                                      max_date=today + timedelta(days=365),
                                      locale='ru')
        bot.send_message(chat_id=call.from_user.id,
                         text='Введи дату заезда',
                         parse_mode='html',
                         reply_markup=calendar)
    except requests.exceptions.ConnectTimeout as exc:
        logger.debug(exc)


@bot.callback_query_handler(func=DetailedTelegramCalendar.func(calendar_id=1))
def handle_arrival_date(call: CallbackQuery) -> None:
    """
    Функция, которая ловит календарь "calendar_id=1" и сохраняет дату заезда в отель,
    выполняется работа календаря для получения дня заезда
    :param call: CallbackQuery
    """
    try:
        today: date = date.today()
        result, key, step = get_calendar(calendar_id=1,
                                         current_date=today,
                                         min_date=today,
                                         max_date=today + timedelta(days=365),
                                         locale='ru',
                                         is_process=True,
                                         callback_data=call)
        if not result and key:
            # Продолжаем отсылать шаги, пока не выберут дату "result"
            bot.edit_message_text(text=f'Выберите {ALL_STEPS[step]}',
                                  chat_id=call.from_user.id,
                                  message_id=call.message.message_id,
                                  reply_markup=key)
        elif result:
            with bot.retrieve_data(user_id=call.from_user.id,
                                   chat_id=call.message.chat.id) as data:
                data['check_in'] = result  # Дата выбрана, сохраняем ее

            bot.edit_message_text(text=f'Дата заезда {result}',
                                  chat_id=call.message.chat.id,
                                  message_id=call.message.message_id)
            bot.send_message(chat_id=call.from_user.id,
                             text='Выберите дату выезда',
                             parse_mode='html')
            # здесь используем вновь полученные данные и генерируем новый календарь
            calendar, step = get_calendar(calendar_id=2,
                                          min_date=result + timedelta(days=1),
                                          max_date=result + timedelta(days=365),
                                          locale="ru")
            bot.send_message(chat_id=call.from_user.id,
                             text=f'Выберите {ALL_STEPS[step]}',
                             reply_markup=calendar)
    except requests.exceptions.ConnectTimeout as exc:
        logger.debug(exc)


@bot.callback_query_handler(func=DetailedTelegramCalendar.func(calendar_id=2))
def handle_departure_date(call: CallbackQuery) -> None:
    """
    Функция, которая ловит календарь "calendar_id=2" и сохраняет дату выезда из отеля,
    выполняется работа календаря для получения дня выезда,
    запускается функция для создания списка отелей,
    в зависимости от выбранной пользователем команды запускает дальнейший
    алгоритм опроса пользователя
    :param call: CallbackQuery
    """
    try:
        with bot.retrieve_data(user_id=call.from_user.id,
                               chat_id=call.message.chat.id) as data:
            day: timedelta = data['check_in'] + timedelta(days=1)
        result, key, step = get_calendar(calendar_id=2,
                                         current_date=day,
                                         min_date=day,
                                         max_date=day + timedelta(days=365),
                                         locale="ru",
                                         is_process=True,
                                         callback_data=call)
        if not result and key:
            # Продолжаем отсылать шаги, пока не выберут дату - "result"
            bot.edit_message_text(text=f'Выберите {ALL_STEPS[step]}',
                                  chat_id=call.from_user.id,
                                  message_id=call.message.message_id,
                                  reply_markup=key)
        elif result:
            with bot.retrieve_data(user_id=call.from_user.id,
                                   chat_id=call.message.chat.id) as data:
                data['check_out'] = result  # Дата выбрана, сохраняем ее
                data['number_day'] = (data['check_out'] - data['check_in']).days

            bot.edit_message_text(text=f'Дата выезда: {result}. Подожди немного...Веду поиск',
                                  chat_id=call.message.chat.id,
                                  message_id=call.message.message_id)

            my_api.hotel_founding(user_id=call.from_user.id, chat_id=call.message.chat.id)
            # здесь делаем проверки на введенную команду, чтобы иди дальше по одной из веток логики.
            if data['command'] in ['/lowprice', '/highprice']:
                bot.set_state(user_id=call.from_user.id,
                              state=SearchInfoState.number_hotels,
                              chat_id=call.message.chat.id)
                bot.send_message(chat_id=call.from_user.id,
                                 text=f'Введите количество отелей для поиска\n'
                                      f'(не более {MAX_NUM_HOTELS})',
                                 parse_mode='html')
            elif data['command'] == '/bestdeal':
                bot.set_state(user_id=call.from_user.id,
                              state=SearchInfoState.price_min,
                              chat_id=call.message.chat.id)
                with bot.retrieve_data(user_id=call.from_user.id,
                                       chat_id=call.message.chat.id) as data:
                    bot.send_message(chat_id=call.from_user.id,
                                     text=f'Введи диапазон цен.\n'
                                          f'Сначала минимальную цену за одни сутки.\n'
                                          f'Фактическая минимальная цена за один день в выбранной локации '
                                          f'{data["min_price_real"]} руб',
                                     parse_mode='html')
    except requests.exceptions.ConnectTimeout as exc:
        logger.debug(exc)


@bot.message_handler(state=SearchInfoState.number_hotels)
def number_hotels(message: Message) -> None:
    """
    Функция, принимающая состояние "number_hotels",
    сохраняет количество отелей, введенных пользователем
    и задает вопрос о необходимости вывода фотографий
    :param message: Message
    """
    try:
        if message.text.isdigit() and MAX_NUM_HOTELS >= int(message.text) > 0:
            bot.send_message(chat_id=message.from_user.id,
                             text='Спасибо, записал. Показать фотографии отелей?',
                             parse_mode='html',
                             reply_markup=yes_no())
            with bot.retrieve_data(user_id=message.from_user.id,
                                   chat_id=message.chat.id) as data:
                data['number_hotels'] = message.text
        else:
            bot.send_message(chat_id=message.from_user.id,
                             text=f'Количество отелей должно быть целым числом '
                                  f'больше 0 и не более {MAX_NUM_HOTELS}',
                             parse_mode='html')
    except requests.exceptions.ConnectTimeout as exc:
        logger.debug(exc)


@bot.callback_query_handler(func=lambda call: True)
def callback_yes_no(call: CallbackQuery) -> None:
    """
    Функция, которая ловит ответ с инлайн - кнопок (ДА, НЕТ),
    и определяет необходимость вывода фотографий и далее
    запрашивает у пользователя количество фотографий
    :param call: CallbackQuery
    """
    try:
        if call.data == 'yes':
            bot.edit_message_text(text=f'Отлично!!! Какое количество фотографий вывести?\n'
                                       f'(не более {MAX_NUM_PHOTOS})',
                                  chat_id=call.message.chat.id,
                                  message_id=call.message.message_id,
                                  parse_mode='html',
                                  reply_markup=None)
            bot.set_state(user_id=call.from_user.id,
                          state=SearchInfoState.number_photos,
                          chat_id=call.message.chat.id)
        elif call.data == 'no':
            bot.edit_message_text(text='Ну ладно, не надо так не надо',
                                  chat_id=call.message.chat.id,
                                  message_id=call.message.message_id,
                                  parse_mode='html',
                                  reply_markup=None)
            with bot.retrieve_data(user_id=call.from_user.id,
                                   chat_id=call.message.chat.id) as data:
                data['number_photos'] = 'Не требуется'
            get_info_hotel(call, is_rejection=True)

    except requests.exceptions.ConnectTimeout as exc:
        logger.debug(exc)


@bot.message_handler(state=SearchInfoState.number_photos)
def number_photos(message: Message) -> None:
    """
    Функция, принимающая состояние "number_photos",
    сохраняет количество фотографий, введенных пользователем
    и запускает функцию с выводом информации по найденным отелям
    :param message: Message
    """
    try:
        if message.text.isdigit() and (MAX_NUM_PHOTOS >= int(message.text) > 0):
            bot.send_message(chat_id=message.from_user.id,
                             text='Отлично! Записал!',
                             parse_mode='html')
            with bot.retrieve_data(user_id=message.from_user.id,
                                   chat_id=message.chat.id) as data:
                data['number_photos'] = message.text
            get_info_hotel(message=message)
        else:
            bot.send_message(chat_id=message.from_user.id,
                             text=f'Количество фотографий должно быть целым числом и больше 0 и не более '
                                  f'{MAX_NUM_PHOTOS}',
                             parse_mode='html')
    except requests.exceptions.ConnectTimeout as exc:
        logger.debug(exc)


@bot.message_handler(state=SearchInfoState.price_min)
def price_minimum(message: Message) -> None:
    """
    Функция, принимающая состояние "price_min",
    сохраняет минимальную цену, введенную пользователем
    и запрашивает максимальную цену поиска
    :param message: Message
    """
    try:
        if message.text.isdigit() and int(message.text) > 0:
            with bot.retrieve_data(user_id=message.from_user.id,
                                   chat_id=message.chat.id) as data:
                data['price_min'] = message.text
                if int(data['price_min']) > float(data['min_price_real']):
                    min_price: str = data['price_min']
                else:
                    min_price: str = data['min_price_real']
                bot.send_message(chat_id=message.from_user.id,
                                 text=f'Ок, записал! Теперь введи максимальную цену за сутки,\n'
                                      f'она должна быть больше {min_price} руб',
                                 parse_mode='html')
                bot.set_state(user_id=message.from_user.id,
                              state=SearchInfoState.price_max,
                              chat_id=message.chat.id)
        else:
            bot.send_message(chat_id=message.from_user.id,
                             text=f'Минимальная цена должна быть целым числом и больше 0',
                             parse_mode='html')
    except requests.exceptions.ConnectTimeout as exc:
        logger.debug(exc)


@bot.message_handler(state=SearchInfoState.price_max)
def price_maximum(message: Message) -> None:
    """
    Функция, принимающая состояние "price_max",
    сохраняет максимальную цену, введенную пользователем
    и запускае функцию для определения минимального расстояния
    из списка отелей от центра и которая запрашивает ввод
    расстояние от центра города для дальнейшего поиска
    :param message: Message
    """
    try:
        if message.text.isdigit() and int(message.text) > 0:
            with bot.retrieve_data(user_id=message.from_user.id,
                                   chat_id=message.chat.id) as data:
                data['price_max'] = message.text
            my_api.get_distance_best(message=message)
        else:
            bot.send_message(chat_id=message.from_user.id,
                             text='Максимальная цена должна быть целым числом и больше 0',
                             parse_mode='html')
    except requests.exceptions.ConnectTimeout as exc:
        logger.debug(exc)


@bot.message_handler(state=SearchInfoState.distance_range)
def distance_range(message: Message) -> None:
    """
    Функция, принимающая состояние "distance_range",
    сохраняет расстояние от центра города, введенное пользователем
     и запрашивает ввод количества отелей для дальнейшего поиска
    :param message: Message
    """
    try:
        with bot.retrieve_data(user_id=message.from_user.id,
                               chat_id=message.chat.id) as data:
            if message.text.isdigit() and int(message.text) > float(data['min_distance_real']):
                data['distance_range'] = message.text
                bot.send_message(chat_id=message.from_user.id,
                                 text=f'Введите количество отелей для поиска\n'
                                      f'(не более {MAX_NUM_HOTELS})',
                                 parse_mode='html')
                bot.set_state(user_id=message.from_user.id,
                              state=SearchInfoState.number_hotels,
                              chat_id=message.chat.id)
                hotels_info = my_api.get_hotels_best(hotels_info=data['hotels_info'],
                                                     distance=data['distance_range'])
                data['hotels_info'] = hotels_info
            else:
                bot.send_message(chat_id=message.from_user.id,
                                 text='Расстояние от центра должно быть целым числом и больше минимального расстояния',
                                 parse_mode='html')
    except requests.exceptions.ConnectTimeout as exc:
        logger.debug(exc)
