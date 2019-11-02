import requests
import re
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


class Destinations(Enum):
    MARINA_RISHHA = 'https://transport.lanit.ru/m/table'
    PLOSHHAD_ILICHA = 'https://transport.lanit.ru/p/table'
    RIZHSKAJA = 'https://transport.lanit.ru/r/table'


class LanitBusInfo:
    @staticmethod
    def get_schedule_info(destinations: Destinations):
        logging.info('Get schedule info started...')
        response = requests.get(destinations.value)

        soup = BeautifulSoup(response.text, 'html.parser')
        tables: List[Tag] = soup.findAll("div", {"class": "col-xs-6"})
        schedule_data = {}
        for table in tables:
            destination_tag: Tag = table.find(
                "div", {"class": "row text-center"})
            destination_text = destination_tag.text.strip()
            time_data = re.findall('([0-9]{2}:[0-9]{2})', str(table))
            schedule_data[destination_text] = time_data

        logging.info(f'schedule_data {type(schedule_data)} = {schedule_data}')
        logging.info('Get schedule info completed')
        return schedule_data


if __name__ == "__main__":
    marina = LanitBusInfo.get_schedule_info(Destinations.MARINA_RISHHA)
    logging.info(f'marina {type(marina)} = {marina}')
    ilicha = LanitBusInfo.get_schedule_info(Destinations.PLOSHHAD_ILICHA)
    logging.info(f'ilicha {type(ilicha)} = {ilicha}')
    rizhskaja = LanitBusInfo.get_schedule_info(Destinations.RIZHSKAJA)
    logging.info(f'rizhskaja {type(rizhskaja)} = {rizhskaja}')