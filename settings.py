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

try:
    bot_token = os.environ['TELEGRAM_TOKEN']
except KeyError as e:
    logging.error(e)
    bot_token = 'token'
time_delta_shift = 3
days = ["понедельник", "вторник", "среда", "четверг", "пятница",
        "суббота", "воскресенье"]
