from datetime import datetime
from bs4 import BeautifulSoup
from bs4.element import Tag
from typing import List
from enum import Enum

import logging
import requests
import re

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
        self.location_char = url

    def __str__(self):
        return f'Location | name:{self.name} location_char:{self.location_char}'


class Locations(Enum):
    MARINA_RISHHA = Location(
        'Марьина роща', 'm')
    PLOSHHAD_ILICHA = Location(
        'Площадь Ильича', 'p')
    RIZHSKAJA = Location('Рижская', 'r')


class Destinations(Enum):
    TO_METRO = 'к метро'
    TO_OFFICE = 'в офис'


class LanitBusInfo:
    @staticmethod
    def get_formated_datetime_text() -> str:
        days = ["понедельник", "вторник", "среда",
                "четверг", "пятница", "суббота", "воскресенье"]
        current_datetime = datetime.now()
        formated_current_time = f'{str(current_datetime.hour).zfill(2)}:{str(current_datetime.minute).zfill(2)}'
        return f'Сейчас {days[datetime.today().weekday()]} {formated_current_time}'

    @staticmethod
    def get_schedule_info(location: Locations) -> dict:
        logging.info('Get schedule info started...')
        response = requests.get(
            f'https://transport.lanit.ru/{location.value.location_char}/table')

        current_datetime = datetime.now()
        soup = BeautifulSoup(response.text, 'html.parser')
        tables: List[Tag] = soup.findAll("div", {"class": "col-xs-6"})
        schedule_data = {}
        for table in tables:
            location_tag: Tag = table.find(
                "div", {"class": "row text-center"})
            destination_text = location_tag.text.strip().lower()
            unparsed_time_data = re.findall('([0-9]{2}:[0-9]{2})', str(table))
            parsed_time_data = []
            for bus_time in unparsed_time_data:
                hour, minute = bus_time.split(':')
                bus_datetime = datetime(year=current_datetime.year,
                                        month=current_datetime.month,
                                        day=current_datetime.day,
                                        hour=int(hour),
                                        minute=int(minute),
                                        second=0)
                logging.debug(
                    f'bus_datetime {type(bus_datetime)} = {bus_datetime}')
                parsed_time_data.append(bus_datetime)
            schedule_data[Destinations(destination_text)] = parsed_time_data

        logging.info(f'schedule_data {type(schedule_data)} = {schedule_data}')
        logging.info('Get schedule info completed')
        return schedule_data

    @staticmethod
    def get_nearest_bus(location: Locations, destinations: Destinations) -> str:
        logging.info('Getting nearest bus started...')
        current_datetime = datetime.now()
        formated_current_time = f'{current_datetime.hour}:{current_datetime.minute}'
        if datetime.today().weekday() > 4:
            logging.info('Getting nearest bus completed')
            return f'{LanitBusInfo.get_formated_datetime_text()}. Сегодня маршруток {destinations.value} {location.value.name} не будет.'
        else:
            schedule_data = LanitBusInfo.get_schedule_info(location)
            if len(schedule_data[destinations]) > 0:
                for bus_datetime in schedule_data[destinations]:
                    if current_datetime < bus_datetime:
                        formated_bus_time = f'{str(bus_datetime.hour).zfill(2)}:{str(bus_datetime.minute).zfill(2)}'
                        time_difference = bus_datetime - current_datetime
                        time_difference_in_minutes = time_difference.total_seconds() / 60
                        logging.info('Getting nearest bus completed')
                        return f'{LanitBusInfo.get_formated_datetime_text()}. Ближайшая маршрутка {destinations.value} {location.value.name} будет через {time_difference_in_minutes} минут в {formated_bus_time}'
                logging.info('Getting nearest bus completed')
                return f'{LanitBusInfo.get_formated_datetime_text()}. Сегодня маршруток {destinations.value} {location.value.name} уже не будет.'
            else:
                logging.info('Getting nearest bus completed')
                return f'{LanitBusInfo.get_formated_datetime_text()}. К сожалению не удалось получить расписание маршруток {destinations.value} {location.value.name}.'


if __name__ == "__main__":
    print(LanitBusInfo.get_nearest_bus(
        Locations.PLOSHHAD_ILICHA, Destinations.TO_METRO))
    print(LanitBusInfo.get_nearest_bus(
        Locations.MARINA_RISHHA, Destinations.TO_OFFICE))
