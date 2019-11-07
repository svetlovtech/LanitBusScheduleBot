from datetime import datetime
from enum import Enum

import requests

import settings
from settings import logging


class Locations(Enum):
    MARINA_ROSHHA = 'm'
    PLOSHHAD_ILICHA = 'p'
    RIZHSKAJA = 'r'


class Destination:
    def __init__(self, api_string: str, translate: str):
        self.api_string = api_string
        self.translate = translate

    def __str__(self):
        return f'Destination | api_string:{self.api_string} translate:{self.translate}'


class Destinations(Enum):
    TO_METRO = Destination('to_metro', 'к')
    TO_OFFICE = Destination('to_office', 'от')


class LanitBusInfo:
    @staticmethod
    def get_nearest_bus(location: Locations, destination: Destinations) -> str:
        logging.info('Getting nearest bus started...')
        response = requests.get(
            f'https://transport.lanit.ru/api/times/{location.value}').json()
        if datetime.today().weekday() > 4:
            message_format = f'Сейчас {settings.days[datetime.today().weekday()]} {response["info"]["now"]}. ' \
                             f'Сегодня маршруток {destination.value.translate} {response["info"]["name"]} не будет.'
            logging.debug(f'message_format {type(message_format)} = {message_format}')
            logging.info('Getting nearest bus completed')
            return message_format
        elif response['time'][destination.value.api_string]['nearest'] is not False:
            message_format = f'Сейчас {settings.days[datetime.today().weekday()]} {response["info"]["now"]}. ' \
                             f'Ближайшая маршрутка {destination.value.translate} ' \
                             f'{response["info"]["name"]} будет через {response["time"][destination.value.api_string]["left"]} ' \
                             f'в {response["time"][destination.value.api_string]["nearest"]}.'

            if response["time"][destination.value.api_string]["next"] is not False:
                message_format = f'{message_format}\n' \
                                 f'Следующая будет в {response["time"][destination.value.api_string]["next"]}.'
            if response['info']['warning'] is not False:
                message_format = f"{message_format}\n" \
                                 f"Предупреждение: {response['info'][destination.value.api_string]['warning']}"
            logging.debug(f'message_format {type(message_format)} = {message_format}')
            logging.info('Getting nearest bus completed')
            return message_format
        elif response['time'][destination.value.api_string]['nearest'] is False:

            message_format = f'Сейчас {settings.days[datetime.today().weekday()]} {response["info"]["now"]}. ' \
                             f'Сегодня маршруток {destination.value.translate} {response["info"]["name"]} не будет.'
            if response['info']['warning'] is not False:
                message_format = f"Предупреждение: {response['info'][destination.value.api_string]['warning']}"
            logging.debug(f'message_format {type(message_format)} = {message_format}')
            logging.info('Getting nearest bus completed')
            return message_format
        else:
            message_format = 'К сожалению не удалось получить расписание'
            return message_format
