import telebot
from telebot import types

bot = telebot.TeleBot('token')


@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_message(
        message.chat.id,
        '''Добро пожаловать. ✌
        Теперь вы можете посмотреть расписание!
		''',
        reply_markup=keyboard())


@bot.message_handler(content_types=["text"])
def send_anytext(message):
    chat_id = message.chat.id
    if message.text == '📖 Расписание':  # В данную функцию можно добавить  обработчик который будет уже проверять
        # дальше нажатия
        text = '✅ Выберете вашу станцию метро \n\n'
        bot.send_message(chat_id, text, parse_mode='HTML', reply_markup=keyboard2())


def keyboard():
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    btn1 = types.KeyboardButton('📖 Расписание')
    markup.add(btn1)
    return markup


def keyboard2():
    BusKey = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    btn2 = types.KeyboardButton('Рижская')
    # btn3 = types.KeyboardButton('Алексеевская')
    btn4 = types.KeyboardButton('Площадь Ильича')
    btn5 = types.KeyboardButton('Марьина роща')
    BusKey.add(btn2, btn4, btn5)
    return BusKey


if __name__ == "__main__":
    bot.polling(none_stop=True)
