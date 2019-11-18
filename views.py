from settings import logging, debug_mode, user_sessions
from models import Models, Locations, Destinations
from bus_schedule import LanitBusInfo
from telebot import types, TeleBot

# -=-=-=-=-=-=-=-=-=-=-=-=- COMMONS VIEWS -=-=-=-=-=-=-=-=-=-=-=-=-


class View():
    def __init__(self, user_session: dict = None):
        logging.debug(f'{type(self).__name__} | Init started...')
        self._user_session = user_session
        self._keyboard = types.InlineKeyboardMarkup()
        self._create_keyboard_header()
        self._create_keyboard_content()
        self._create_keyboard_footer()
        self._message_text = self._set_message_text()
        logging.debug(f'{type(self).__name__} | Init complited')

    def _create_keyboard_header(self):
        logging.debug(
            f'{type(self).__name__} | Creating keyboard header started...')
        buttons = []
        # if debug_mode:
        #     user_session_button = types.InlineKeyboardButton(
        #         text="user session", callback_data=encode_data(GetUserInfo.__name__))
        #     buttons.append(user_session_button)
        self._keyboard.add(*buttons)
        logging.debug(
            f'{type(self).__name__} | Creating keyboard header completed')

    def _create_keyboard_content(self):
        logging.debug(
            f'{type(self).__name__} | Create keyboard content started...')
        # Put your action here
        logging.debug(
            f'{type(self).__name__} | Create keyboard content completed')

    def _create_keyboard_footer(self):
        logging.debug(
            f'{type(self).__name__} | Create keyboard footer started...')
        buttons = []
        if type(self).__name__ is not HelpMenu.__name__:
            buttons.append(types.InlineKeyboardButton(
                text="Помощь", callback_data=encode_data(HelpMenu.__name__)))
        if type(self).__name__ is not StartMenu.__name__:
            buttons.append(types.InlineKeyboardButton(
                text="На главную", callback_data=encode_data(StartMenu.__name__)))
        self._keyboard.add(*buttons)

        logging.debug(
            f'{type(self).__name__} | Create keyboard footer completed')

    def _set_message_text(self):
        return 'BASIC VIEW'

    def get_message_text(self):
        return self._message_text

    def get_keyboard(self):
        return self._keyboard


class StartMenu(View):
    def _create_keyboard_content(self):
        logging.debug(
            f'{type(self).__name__} | Create keyboard content started...')
        select_destination_button = types.InlineKeyboardButton(
            text="Узнать расписание", callback_data=encode_data(GetBusSchedule.__name__))

        self._keyboard.add(select_destination_button)
        logging.debug(
            f'{type(self).__name__} | Create keyboard content completed')

    def _set_message_text(self):
        return "Данный бот предоставляет расписание маршруток компании ЛАНИТ (г. Москва, ул. Мурманский проезд 14к1)."


class HelpMenu(View):
    def _create_keyboard_content(self):
        logging.debug(
            f'{type(self).__name__} | Create keyboard content started...')
        switch_button = types.InlineKeyboardButton(
            text='Создатель', url="https://t.me/ASvetlov92")
        btn_my_site = types.InlineKeyboardButton(
            text='GitHub', url='https://github.com/32-52/LanitBusScheduleBot')
        self._keyboard.add(switch_button, btn_my_site)
        logging.debug(
            f'self._keyboard {type(self._keyboard)} = {self._keyboard}')
        logging.debug(
            f'{type(self).__name__} | Create keyboard content completed')

    def _set_message_text(self):
        return "Если возникли проблемы с ботом или есть предложения по улучшению, то свяжитесь со мной\nЕсли этот бот оказался полезен, то буду очень рад звездочке"


class GetUserInfo(View):
    def _create_keyboard_content(self):
        logging.debug(
            f'{type(self).__name__} | Create keyboard content started...')
        logging.debug(
            f'self._keyboard {type(self._keyboard)} = {self._keyboard}')
        logging.debug(
            f'{type(self).__name__} | Create keyboard content completed')

    def _set_message_text(self):
        return str(user_sessions)

# -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-

# -=-=-=-=-=-=-=-=-=-=-=-=- BUSSCHEDULES VIEWS -=-=-=-=-=-=-=-=-=-=-=-=-


class GetBusSchedule(View):
    pass


class SelectDestination(GetBusSchedule):
    def _create_keyboard_content(self):
        logging.debug(
            f'{type(self).__name__} | Create keyboard content started...')
        buttons = []
        for destination in Destinations:
            buttons.append(types.InlineKeyboardButton(
                text=destination.value, callback_data=encode_data(GetBusSchedule.__name__, destination)))
        self._keyboard.add(*buttons)
        logging.debug(
            f'self._keyboard {type(self._keyboard)} = {self._keyboard}')
        logging.debug(
            f'{type(self).__name__} | Create keyboard content completed')

    def _set_message_text(self):
        return "Куда нужно ехать?"


class SelectLocation(GetBusSchedule):
    def _create_keyboard_content(self):
        logging.debug(
            f'{type(self).__name__} | Create keyboard content started...')
        buttons = []
        for location in Locations:
            buttons.append(types.InlineKeyboardButton(
                text=location.value, callback_data=encode_data(GetBusSchedule.__name__, location)))
        self._keyboard.add(*buttons)
        logging.debug(
            f'self._keyboard {type(self._keyboard)} = {self._keyboard}')
        logging.debug(
            f'{type(self).__name__} | Create keyboard content completed')

    def _set_message_text(self):
        return "Какое метро нам нужно?"


class ShowSheduleResult(GetBusSchedule):
    def _create_keyboard_content(self):
        shedule_site_button = types.InlineKeyboardButton(
            text='Посмотреть на сайте', url='https://transport.lanit.ru/')
        self._keyboard.add(shedule_site_button)

    def _set_message_text(self):
        return LanitBusInfo.get_nearest_bus(location=self._user_session['Locations'],
                                            destination=self._user_session['Destinations'])

# -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-


# -=-=-=-=-=-=-=-=-=-=-=-=- ENCODE DECODE CALLBACK DATA -=-=-=-=-=-=-=-=-=-=-=-=-

def decode_data(data: str):
    logging.debug(f'data {type(data)} = {data}')
    splitted_data = data.split('|')
    view_class_name_str = splitted_data[0]
    logging.debug(
        f'view_class_name_str {type(view_class_name_str)} = {view_class_name_str}')

    model_class_name_str = splitted_data[1]
    logging.debug(
        f'model_class_name_str {type(model_class_name_str)} = {model_class_name_str}')

    model_value_str = splitted_data[2]
    logging.debug(
        f'model_value_str {type(model_value_str)} = {model_value_str}')

    view_class = None
    model_class = None
    model_value = None

    for cls in View.__subclasses__():
        if cls.__name__ in view_class_name_str:
            view_class = cls
            break

    if model_class_name_str is not None and model_value_str is not None:
        for cls in Models.__subclasses__():
            if cls.__name__ in model_class_name_str:
                model_value = cls(model_value_str)
                break
        return (view_class, model_value)
    else:
        return(view_class, None)


def encode_data(view_class: View, model_class: Models = None):
    logging.debug(f'view_class {view_class}')
    logging.debug(f'model_class {type(model_class)} = {model_class}')
    if model_class is not None:
        return f'{view_class}|{type(model_class).__name__}|{model_class.value}'
    else:
        return f'{view_class}|None|None'
# -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
