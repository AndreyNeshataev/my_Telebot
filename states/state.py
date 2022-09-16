from telebot.handler_backends import State, StatesGroup


class SearchInfoState(StatesGroup):
    command = State()
    name = State()
    city = State()
    destinationID = State()
    number_hotels = State()
    number_photos = State()
    min_price_real = State()
    hotels_info = State()
    price_min = State()
    price_max = State()
    min_distance_real = State()
    distance_range = State()

