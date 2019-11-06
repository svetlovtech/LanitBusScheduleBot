import logging
import re
from datetime import datetime, timedelta
from enum import Enum
from typing import List
import os
import pymorphy2
import requests
import telebot
from bs4 import BeautifulSoup
from bs4.element import Tag
from telebot import types
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
if 'token' in bot_token:
    bot_token = os.environ['TELEGRAM_TOKEN']
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


def keyboard_after_all():
    markup = ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    markup.add("/start")
    return markup


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


@bot.callback_query_handler(func=lambda call: call.data == "metro" or call.data == "office" or call.data == "mainmenu")
def select_location_step(call):
    if call.data == "mainmenu":
        keyboardmain = types.InlineKeyboardMarkup(row_width=2)
        first_button = types.InlineKeyboardButton(text="к метро", callback_data="metro")
        second_button = types.InlineKeyboardButton(text="в офис", callback_data="office")
        keyboardmain.add(first_button, second_button)
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Куда поедем?",
                              reply_markup=keyboardmain)

    if call.data == "metro":
        keyboard = types.InlineKeyboardMarkup()
        rele1 = types.InlineKeyboardButton(text="Марьина роща", callback_data="m")
        rele2 = types.InlineKeyboardButton(text="Рижская", callback_data="r")
        rele3 = types.InlineKeyboardButton(text="Площадь Ильича", callback_data="p")
        backbutton = types.InlineKeyboardButton(text="назад", callback_data="mainmenu")
        keyboard.add(rele1, rele2, rele3, backbutton)
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text='Какое метро нужно?', reply_markup=keyboard)

    if call.data == "office":
        keyboard = types.InlineKeyboardMarkup()
        rele1 = types.InlineKeyboardButton(text="Марьина роща", callback_data="m_o")
        rele2 = types.InlineKeyboardButton(text="Рижская", callback_data="r_o")
        rele3 = types.InlineKeyboardButton(text="Площадь Ильича", callback_data="p_o")
        backbutton = types.InlineKeyboardButton(text="назад", callback_data="mainmenu")
        keyboard.add(rele1, rele2, rele3, backbutton)
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text='С какого метро едем?', reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: call.data == "m" or call.data == "r" or call.data == 'p' or
                                              call.data == "m_o" or call.data == "r_o" or call.data == 'p_o')
def select_destination_step_metro(call):
    keyboard = types.InlineKeyboardMarkup()
    backbutton = types.InlineKeyboardButton(text="Попробовать еще раз", callback_data="mainmenu")
    keyboard.add(backbutton)

    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                          text=LanitBusInfo.get_nearest_bus(
                              location=Locations.MARINA_RISHHA if 'm' in call.data else Locations.RIZHSKAJA
                              if 'r' in call.data else Locations.PLOSHHAD_ILICHA,
                              destinations=Destinations.TO_METRO if '_o' not in call.data else Destinations.TO_OFFICE),
                          reply_markup=keyboard)


@bot.message_handler(commands=['start'])
def on_start(message):
    keyboardmain = types.InlineKeyboardMarkup(row_width=2)
    first_button = types.InlineKeyboardButton(text="к метро", callback_data="metro")
    second_button = types.InlineKeyboardButton(text="в офис", callback_data="office")
    keyboardmain.add(first_button, second_button)
    bot.send_message(message.chat.id, "Куда поедем?", reply_markup=keyboardmain)


@bot.message_handler(func=lambda message: False if 'help' in message.text else True)
def echo_message(message):
    bot.reply_to(message, 'Не могу найти такую команду :(\nПопробуйте /start')


@bot.message_handler(commands=['help'])
def send_welcome(message):
    bot.send_message(message.chat.id,
                     'Если возникли проблемы с ботом или есть предложения по улучшению, то свяжитесь со мной'
                     ' @ASvetlov92.\nЕсли этот бот оказался полезен, то буду очень рад звездочке'
                     ' https://github.com/32-52/LanitBusScheduleBot')


if __name__ == "__main__":
    while True:
        try:
            bot.polling(none_stop=True)
        except Exception as e:
            logging.warning(e)
            continue
