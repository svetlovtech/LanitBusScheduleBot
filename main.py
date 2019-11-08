from enum import Enum

from telebot import types, TeleBot

import settings
from bus_schedule import LanitBusInfo, Locations, Destinations
from settings import logging


def keyboard_after_all():
    markup = types.ReplyKeyboardMarkup(
        one_time_keyboard=True, resize_keyboard=True)
    markup.add("/start")
    return markup


bot = TeleBot(settings.bot_token)


class Step(Enum):
    SELECT_DESTINATION = 'SELECT_DESTINATION'
    SELECT_LOCATION = 'SELECT_LOCATION'
    GET_SCHEDULE = 'GET_SCHEDULE'


@bot.callback_query_handler(func=lambda
        call: call.data in ["metro", "office", "mainmenu"] or call.data[:4] == "full")
def select_location_step(call):
    if call.data == "mainmenu":
        keyboardmain = types.InlineKeyboardMarkup(row_width=2)
        first_button = types.InlineKeyboardButton(
            text="К метро", callback_data="metro")
        second_button = types.InlineKeyboardButton(
            text="В офис", callback_data="office")
        keyboardmain.add(first_button, second_button)
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Куда поедем?",
                              reply_markup=keyboardmain)

    if call.data == "metro":
        keyboard = types.InlineKeyboardMarkup(row_width=2)
        rele1 = types.InlineKeyboardButton(
            text="Марьина роща", callback_data="m")
        rele2 = types.InlineKeyboardButton(text="Рижская", callback_data="r")
        rele3 = types.InlineKeyboardButton(
            text="Площадь Ильича", callback_data="p")
        backbutton = types.InlineKeyboardButton(
            text="Назад", callback_data="mainmenu")
        keyboard.row(rele3)
        keyboard.add(rele1, rele2, backbutton)
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text='Какое метро нужно?', reply_markup=keyboard)

    if call.data == "office":
        keyboard = types.InlineKeyboardMarkup(row_width=2)
        rele1 = types.InlineKeyboardButton(
            text="Марьина роща", callback_data="m_o")
        rele2 = types.InlineKeyboardButton(text="Рижская", callback_data="r_o")
        rele3 = types.InlineKeyboardButton(
            text="Площадь Ильича", callback_data="p_o")
        backbutton = types.InlineKeyboardButton(
            text="Назад", callback_data="mainmenu")
        keyboard.row(rele3)
        keyboard.add(rele1, rele2, backbutton)
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text='С какого метро едем?', reply_markup=keyboard)

    if call.data[:4] == "full":
        keyboard = types.InlineKeyboardMarkup()
        backbutton = types.InlineKeyboardButton(
            text="Попробовать ещё раз", callback_data="mainmenu")
        keyboard.add(backbutton)
        with open(f'resources/images/{call.data}.jpg', 'rb') as img:
            bot.send_photo(chat_id=call.message.chat.id, photo=img)


@bot.callback_query_handler(func=lambda call: call.data in ["m", "r", 'p', "m_o", "r_o", 'p_o'])
def select_destination_step_metro(call):
    keyboard = types.InlineKeyboardMarkup()
    backbutton = types.InlineKeyboardButton(
        text="Попробовать еще раз", callback_data="mainmenu")
    three_button = types.InlineKeyboardButton(
        text="Полное расписание", callback_data=f"resources/images/fullSchedule_{call.data}")
    keyboard.add(backbutton, three_button)

    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                          text=LanitBusInfo.get_nearest_bus(
                              location=Locations.MARINA_ROSHHA if 'm' in call.data else Locations.RIZHSKAJA
                              if 'r' in call.data else Locations.PLOSHHAD_ILICHA,
                              destination=Destinations.TO_METRO if '_o' not in call.data else Destinations.TO_OFFICE),
                          reply_markup=keyboard)


@bot.message_handler(commands=['start'])
def on_start(message):
    keyboardmain = types.InlineKeyboardMarkup(row_width=2)
    first_button = types.InlineKeyboardButton(
        text="К метро", callback_data="metro")
    second_button = types.InlineKeyboardButton(
        text="В офис", callback_data="office")
    keyboardmain.add(first_button, second_button)
    bot.send_message(message.chat.id, "Куда поедем?",
                     reply_markup=keyboardmain)


@bot.message_handler(func=lambda message: False if 'help' in message.text else True)
def echo_message(message):
    bot.reply_to(message, 'Не могу найти такую команду :(\nПопробуйте /start')


@bot.message_handler(commands=['help'])
def send_welcome(message):
    markup = types.InlineKeyboardMarkup()
    switch_button = types.InlineKeyboardButton(text='Создатель', url="https://t.me/ASvetlov92")
    btn_my_site = types.InlineKeyboardButton(text='GitHub', url='https://github.com/32-52/LanitBusScheduleBot')
    markup.add(switch_button, btn_my_site)
    bot.send_message(message.chat.id,
                     "Если возникли проблемы с ботом или есть предложения по улучшению, то свяжитесь со мной🤔\n"
                     "Если этот бот оказался полезен, то буду очень рад звездочке⭐",
                     reply_markup=markup)


if __name__ == "__main__":
    while True:
        try:
            bot.polling(none_stop=True)
        except Exception as e:
            logging.warning(e)
            continue
