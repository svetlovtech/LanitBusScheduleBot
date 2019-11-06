from enum import Enum

import logging
import os

logging.basicConfig(
    level=logging.DEBUG,
    format="[%(asctime)s] %(levelname)-12s|process:%(process)-5s|thread:%"
           "(thread)-5s|funcName:%(funcName)s|message:%(message)s",
    handlers=[
        # logging.FileHandler('fileName.log'),
        logging.StreamHandler()
    ])

bot_token = os.environ['TELEGRAM_TOKEN']
time_delta_shift = 3
days = ["понедельник", "вторник", "среда", "четверг", "пятница",
        "суббота", "воскресенье"]


class Location:
    def __init__(self, name: str, url: str):
        self.name = name
        self.location_char = url

    def __str__(self):
        return f'Location | name:{self.name} location_char:{self.location_char}'


class Locations(Enum):
    MARINA_RISHHA = Location(
        'Марьина роща', 'm')
    PLOSHHAD_ILICHA = Location(
        'Площадь Ильича', 'p')
    RIZHSKAJA = Location('Рижская', 'r')


class Destination:
    def __init__(self, api_string: str, translate: str):
        self.api_string = api_string
        self.translate = translate

    def __str__(self):
        return f'Destination | api_string:{self.api_string} translate:{self.translate}'


class Destinations(Enum):
    TO_METRO = Destination('to_metro', 'к метро')
    TO_OFFICE = Destination('to_office', 'в офис')
