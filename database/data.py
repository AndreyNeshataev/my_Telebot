from loguru import logger
from peewee import PeeweeException
from database.model import User, db

logger.add('debug.log', format='{time} {level} {message}',
           level='DEBUG', rotation='1MB', compression='zip')


def set_user_data(**kwargs):
    try:
        if not User.table_exists():
            User.create_table()
        with db:
            User.create(name=kwargs['name'],
                        telegram_id=kwargs['telegram_id'],
                        city=kwargs['city'],
                        check_in=kwargs['check_in'],
                        check_out=kwargs['check_out'],
                        hotel=kwargs['hotel'],
                        link=kwargs['link'])
    except PeeweeException as exc:
        logger.debug(exc)


def get_info_data(user_id, name):
    try:
        with db:
            query = User.select().where(User.telegram_id == user_id and User.name == name.capitalize()). \
                limit(10).order_by(User.id.desc())
            return query
    except (PeeweeException, LookupError) as exc:
        logger.debug(exc)
