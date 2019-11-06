from settings import logging, Locations, Destinations, Location
from datetime import datetime, timedelta

import requests
import settings


class LanitBusInfo:
    @staticmethod
    def get_nearest_bus(location: Locations, destinations: Destinations) -> str:
        logging.info('Getting nearest bus started...')
        current_datetime = datetime.now() + timedelta(hours=settings.time_delta_shift)
        response = requests.get(
            f'https://transport.lanit.ru/api/times/{location.value.location_char}').json()

        if datetime.today().weekday() > 4:
            logging.info('Getting nearest bus completed')
            return f'Сейчас {settings.days[datetime.today().weekday()]} {response["info"]["now"]}. Сегодня маршруток ' \
                   f'{destinations.value} {response["info"]["name"]} не будет.'
        else:
            schedule_data = LanitBusInfo.get_schedule_info(location)
            if len(schedule_data[destinations]) > 0:
                for bus_datetime in schedule_data[destinations]:
                    if current_datetime < bus_datetime:
                        formated_bus_time = f'{str(bus_datetime.hour).zfill(2)}:{str(bus_datetime.minute).zfill(2)}'
                        time_difference = bus_datetime - current_datetime
                        time_difference_in_minutes = time_difference.total_seconds() / 60
                        logging.info('Getting nearest bus completed')
                        return f'{LanitBusInfo.get_formated_datetime_text()}. Ближайшая маршрутка' \
                               f' {destinations.value} {location.value.name} будет через' \
                               f' {int(time_difference_in_minutes)} {response["info"]["name"]} в {formated_bus_time}'
                logging.info('Getting nearest bus completed')
                return f'{LanitBusInfo.get_formated_datetime_text()}. Сегодня маршруток {destinations.value}' \
                       f' от {location.value.name} уже не будет.'
            else:
                logging.info('Getting nearest bus completed')
                return f'{LanitBusInfo.get_formated_datetime_text()}. К сожалению не удалось получить расписание' \
                       f' маршруток {destinations.value} {location.value.name}.'
