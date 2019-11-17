from models import Destinations, Locations
from settings import logging
from datetime import datetime
import requests
import settings


class LanitBusInfo:
    @staticmethod
    def get_nearest_bus(location: Locations, destination: Destinations) -> str:
        logging.info('Getting nearest bus started...')

        location_data = None
        if location == Locations.MARINA_ROSHHA:
            location_data = 'm'
        elif location == Locations.PLOSHHAD_ILICHA:
            location_data = 'p'
        elif location == Locations.RIZHSKAJA:
            location_data = 'r'

        destination_data = None
        if destination == Destinations.TO_METRO:
            destination_data = 'to_metro'
        elif destination == Destinations.TO_OFFICE:
            destination_data = 'to_office'
            
        response = requests.get(
            f'https://transport.lanit.ru/api/times/{location_data}').json()

        message_format = f'Сейчас {settings.days[datetime.today().weekday()]} {response["info"]["now"]}\n' \
                         f'Метро: {location.value}\n' \
                         f'Куда: {destination.value}\n'

        if datetime.today().weekday() > 4:
            logging.debug(
                f'message_format {type(message_format)} = {message_format}')
            logging.info('Getting nearest bus completed')
            message_format += 'Сегодня маршруток не будет'
            return message_format
        elif response['time'][destination_data]['nearest'] is not False:

            message_format += f'Ближайшая маршрутка будет через {response["time"][destination_data]["left"]} ' \
                              f'в {response["time"][destination_data]["nearest"]}\n'

            if response["time"][destination_data]["next"] is not False:
                message_format += f'Следующая будет в {response["time"][destination_data]["next"]}\n'
            else:
                message_format += f'Маршруток больше сегодня не будет\n'
                
            if response['info']['warning'] is not False:
                message_format += f"Важно: {response['info'][destination_data]['warning']}"
            logging.debug(
                f'message_format {type(message_format)} = {message_format}')
            logging.info('Getting nearest bus completed')
            return message_format

        elif response['time'][destination_data]['nearest'] is False:
            message_format += f'Сегодня маршруток не будет.\n'
            if response['info']['warning'] is not False:
                message_format += f"Предупреждение: {response['info'][destination_data]['warning']}"
            logging.debug(
                f'message_format {type(message_format)} = {message_format}')
            logging.info('Getting nearest bus completed')
            return message_format
        else:
            message_format = 'К сожалению не удалось получить расписание\n'
            return message_format
