from typing import Dict
from loguru import logger
import requests
from requests import Response
from telebot import logger


def request_to_api(url: str, headers: Dict[str, str], querystring: Dict[str, str]) -> bool | Response:
    """
    Функция для проведения запросов к API
    :param url: str - адресная строка к rapidapi.com
    :param headers: Dict[str, str] - словарь с ключом
    :param querystring: Dict[str, str] - словарь с параметрами к запросу
    :return: bool | Response
    """
    try:
        response: Response = requests.get(url, headers=headers, params=querystring, timeout=30)
        if response.status_code == requests.codes.ok:
            if headers is None and querystring is None:
                return True
            else:
                return response
    except requests.exceptions.RequestException as exc:
        logger.debug(exc)
        logger.add('debug.log', format='{time} {level} {message}',
                   level='DEBUG', rotation='1MB', compression='zip')
