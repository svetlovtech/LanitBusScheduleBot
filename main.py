import logging
import re
from datetime import datetime, timedelta
from enum import Enum
from typing import List

import pymorphy2
import requests
import telebot
from bs4 import BeautifulSoup
from bs4.element import Tag
from telebot.types import ReplyKeyboardMarkup

# -=-=-=-=-=-=-=-=-=-=- Config part -=-=-=-=-=-=-=-=-=-=-=-
logging.basicConfig(
    level=logging.DEBUG,
    format="[%(asctime)s] %(levelname)-12s|process:%(process)-5s|thread:%"
           "(thread)-5s|funcName:%(funcName)s|message:%(message)s",
    handlers=[
        # logging.FileHandler('fileName.log'),
        logging.StreamHandler()
    ])

bot_token = 'token'
time_delta_shift = 3


# -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-


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


def mint(word, number):
    morph = pymorphy2.MorphAnalyzer()
    text = morph.parse(word)[0]
    return text.make_agree_with_number(number).word


class LanitBusInfo:
    @staticmethod
    def get_formated_datetime_text() -> str:
        days = ["понедельник", "вторник", "среда",
                "четверг", "пятница", "суббота", "воскресенье"]
        current_datetime = datetime.now() + timedelta(hours=time_delta_shift)
        formated_current_time = f'{str(current_datetime.hour).zfill(2)}:{str(current_datetime.minute).zfill(2)}'
        return f'Сейчас {days[datetime.today().weekday()]} {formated_current_time}'

    @staticmethod
    def get_schedule_info(location: Locations) -> dict:
        logging.info('Get schedule info started...')
        response = requests.get(
            f'https://transport.lanit.ru/{location.value.location_char}/table')

        current_datetime = datetime.now() + timedelta(hours=time_delta_shift)
        soup = BeautifulSoup(response.text, 'lxml')
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
        current_datetime = datetime.now() + timedelta(hours=time_delta_shift)
        if datetime.today().weekday() > 4:
            logging.info('Getting nearest bus completed')
            return f'{LanitBusInfo.get_formated_datetime_text()}. Сегодня маршруток ' \
                f'{destinations.value} {location.value.name} не будет.'
        else:
            schedule_data = LanitBusInfo.get_schedule_info(location)
            if len(schedule_data[destinations]) > 0:
                for bus_datetime in schedule_data[destinations]:
                    if current_datetime < bus_datetime:
                        formated_bus_time = f'{str(bus_datetime.hour).zfill(2)}:{str(bus_datetime.minute).zfill(2)}'
                        time_difference = bus_datetime - current_datetime
                        time_difference_in_minutes = time_difference.total_seconds() / 60
                        logging.info('Getting nearest bus completed')
                        a = mint("минута", int(time_difference_in_minutes))
                        return f'{LanitBusInfo.get_formated_datetime_text()}. Ближайшая маршрутка' \
                            f' {destinations.value} {location.value.name} будет через' \
                            f' {int(time_difference_in_minutes)} {a} в {formated_bus_time}'
                logging.info('Getting nearest bus completed')
                return f'{LanitBusInfo.get_formated_datetime_text()}. Сегодня маршруток {destinations.value}' \
                    f' от {location.value.name} уже не будет.'
            else:
                logging.info('Getting nearest bus completed')
                return f'{LanitBusInfo.get_formated_datetime_text()}. К сожалению не удалось получить расписание' \
                    f' маршруток {destinations.value} {location.value.name}.'


# -=-=-=-=-=-=-=-=-=-=-=Telegram bot part=-=-=-=-=-=-=-=-=-=-=-
bot = telebot.TeleBot(bot_token)


class Step(Enum):
    SELECT_DESTINATION = 'SELECT_DESTINATION'
    SELECT_LOCATION = 'SELECT_LOCATION'
    GET_SCHEDULE = 'GET_SCHEDULE'


bot_session_data = {}


def select_location_step(message):
    try:
        for location in Locations:
            if message.text == location.value.name:
                bot_session_data[message.from_user.id]["location"] = location
                break
        if bot_session_data[message.from_user.id]["location"] is None:
            raise ValueError('Location is invalid')
        bot.reply_to(
            message,
            f'Давай посмотрим когда будет маршрутка {bot_session_data[message.from_user.id]["destination"].value}'
            f' от {bot_session_data[message.from_user.id]["location"].value.name}...')
        bot.send_message(message.chat.id, LanitBusInfo.get_nearest_bus(
            location=bot_session_data[message.from_user.id]["location"],
            destinations=bot_session_data[message.from_user.id]["destination"]))
        bot.reply_to(message, 'Попробуем еще раз?', reply_markup=keyboard_after_all())
    except ValueError:
        bot.reply_to(message, 'Не знаю такой локации :(')
        bot.send_message(message, 'Попробуем еще раз?', reply_markup=keyboard_after_all())
    except Exception:
        bot.send_message(message.chat.id, 'Кажется что-то пошло не так :(')
        bot.send_message(message.chat.id, 'Попробуем еще раз?', reply_markup=keyboard_after_all())


def keyboard_after_all():
    markup = ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    markup.add("/start")
    return markup


def select_destination_step(message):
    try:
        markup = ReplyKeyboardMarkup(
            one_time_keyboard=True, resize_keyboard=True)
        for location in Locations:
            markup.add(location.value.name)
        destination = Destinations(message.text)
        bot_session_data[message.from_user.id]['destination'] = destination
        location_message = bot.reply_to(
            message, f'Хорошо едем {destination.value}. А какое метро?', reply_markup=markup)
        bot.register_next_step_handler(
            location_message, select_location_step)

    except ValueError:
        bot.reply_to(message, 'Не знаю такого направления :(')
    except Exception:
        bot.send_message(message.chat.id, 'Кажется что-то пошло не так :(')


@bot.message_handler(commands=['start'])
def on_start(message):
    try:
        markup = ReplyKeyboardMarkup(
            one_time_keyboard=True, resize_keyboard=True)
        for destination in Destinations:
            markup.add(destination.value)
        bot.send_message(message.chat.id,
                         'Привет👋\nЭто перезапуск бота расписания маршруток компании'
                         ' ЛАНИТ 🚌\nРасписание только для г.Москва, ул.Мурманский проезд 14к1'
                         ' 🗓\nРасписание маршруток синхронизировано с https://transport.lanit.ru/')
        destination_message = bot.reply_to(
            message, 'Куда поедем?', reply_markup=markup)
        bot_session_data[message.from_user.id] = {}
        bot.register_next_step_handler(
            destination_message, select_destination_step)

    except Exception:
        bot.send_message(message.chat.id, 'Кажется что-то пошло не так :(')


@bot.message_handler(func=lambda message: True)
def echo_message(message):
    bot.reply_to(message, 'Не могу найти такую команду :(\nПопробуйте /start')


@bot.message_handler(commands=['help'])
def send_welcome(message):
    bot.send_message(message.chat.id,
                     'Если возникли проблемы с ботом или есть предложения по улучшению, то свяжитесь со мной'
                     ' @ASvetlov92.\nЕсли этот бот оказался полезен, то буду очень рад звездочке'
                     ' https://github.com/32-52/LanitBusScheduleBot')


if __name__ == "__main__":
    bot.polling(none_stop=True)
