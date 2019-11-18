from settings import logging, user_sessions, bot_token
from telebot import types, TeleBot

import views
import models

bot = TeleBot(bot_token)


@bot.message_handler(commands=['help'])
def help_handler(message):
    view = views.HelpMenu()
    bot.send_message(chat_id=message.chat.id,
                     text=view.get_message_text(),
                     reply_markup=view.get_keyboard())
    

@bot.message_handler(commands=['start'])
def help_handler(message):
    view = views.StartMenu()
    bot.send_message(chat_id=message.chat.id,
                     text=view.get_message_text(),
                     reply_markup=view.get_keyboard())


@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    logging.debug(f'call.data {type(call.data)} = {call.data}')
    view_class, model_class = views.decode_data(call.data)
    
    if call.message.chat.id not in user_sessions:
        logging.info(f'Clearing session {call.message.chat.id}')
        user_sessions[call.message.chat.id] = {}

    if model_class is not None:
        user_sessions[call.message.chat.id][f'{type(model_class).__name__}'] = model_class

    view = view_class()
    if isinstance(view, views.GetBusSchedule):
        if 'Destinations' not in user_sessions[call.message.chat.id]:
            view = views.SelectDestination()
        elif 'Locations' not in user_sessions[call.message.chat.id]:
            view = views.SelectLocation()
        elif 'Destinations' in user_sessions[call.message.chat.id] and 'Locations' in user_sessions[call.message.chat.id]:
            view = views.ShowSheduleResult(user_sessions[call.message.chat.id])
            del user_sessions[call.message.chat.id]['Destinations']
            del user_sessions[call.message.chat.id]['Locations']
        else:
            view = views.StartMenu()

    bot.edit_message_text(chat_id=call.message.chat.id,
                          message_id=call.message.message_id,
                          text=view.get_message_text(),
                          reply_markup=view.get_keyboard())


if __name__ == "__main__":
    bot.polling(none_stop=True)
    # while True:
    #     try:
    #         bot.polling(none_stop=True)
    #     except Exception as e:
    #         logging.warning(e)
    #         continue
