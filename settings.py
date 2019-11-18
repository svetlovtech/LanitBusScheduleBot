import logging
import os

logging.basicConfig(
    level=logging.DEBUG,
    format="[%(asctime)s] %(levelname)-12s|process:%(process)-5s|thread:%"
           "(thread)-5s|funcName:%(funcName)s|message:%(message)s",
    handlers=[
        # logging.FileHandler('fileName.log'),
        logging.StreamHandler()
    ])

user_sessions = {}
days = ["понедельник", "вторник", "среда", "четверг", "пятница",
        "суббота", "воскресенье"]

bot_token = None
debug_mode = None

try:
    bot_token = os.environ['TELEGRAM_TOKEN']
    debug_mode = bool(os.environ['DEBUG_MODE'])
except KeyError as e:
    logging.error(e)
