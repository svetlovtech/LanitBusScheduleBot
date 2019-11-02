import requests
import re
import datetime
from bs4 import BeautifulSoup
from bs4.element import Tag
from typing import List
from enum import Enum
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format="[%(asctime)s] %(levelname)-12s|process:%(process)-5s|thread:%(thread)-5s|funcName:%(funcName)s|message:%(message)s",
    handlers=[
        # logging.FileHandler('fileName.log'),
        logging.StreamHandler()
    ])


class Location:
    def __init__(self, name: str, url: str):
        self.name = name
        self.url = url

    def __str__(self):
        return f'Name:{self.name} url:{self.url}'


class Locations(Enum):
    MARINA_RISHHA = Location(
        'Марьина роща', 'https://transport.lanit.ru/m/table')
    PLOSHHAD_ILICHA = Location(
        'Площадь Ильича', 'https://transport.lanit.ru/p/table')
    RIZHSKAJA = Location('Рижская', 'https://transport.lanit.ru/r/table')


class Destinations(Enum):
    TO_METRO = 'к метро'
    TO_OFFICE = 'к офису'


class LanitBusInfo:
    @staticmethod
    def get_schedule_info(location: Locations) -> dict:
        logging.info('Get schedule info started...')
        response = requests.get(location.value.url)

        soup = BeautifulSoup(response.text, 'html.parser')
        tables: List[Tag] = soup.findAll("div", {"class": "col-xs-6"})
        schedule_data = {}
        for table in tables:
            location_tag: Tag = table.find(
                "div", {"class": "row text-center"})
            destination_text = location_tag.text.strip()
            time_data = re.findall('([0-9]{2}:[0-9]{2})', str(table))
            schedule_data[destination_text] = time_data

        logging.info(f'schedule_data {type(schedule_data)} = {schedule_data}')
        logging.info('Get schedule info completed')
        return schedule_data

    @staticmethod
    def get_nearest_bus(location: Locations, destinations: Destinations) -> str:
        current_time = datetime.datetime.now()
        formated_current_time = f'{current_time.hour}:{current_time.minute}'
        if datetime.datetime.today().weekday() < 5:
            return ''
        else:
            return f'Сейчас {formated_current_time}. Сегодня маршруток {destinations.value} {location.value.name} уже не будет.'


if __name__ == "__main__":
    var_name = datetime.datetime.today().weekday()
    qweasd = LanitBusInfo.get_nearest_bus(
        Locations.PLOSHHAD_ILICHA, Destinations.TO_METRO)
    logging.info(f'qweasd {type(qweasd)} = {qweasd}')
