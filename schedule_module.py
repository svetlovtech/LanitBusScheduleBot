import requests
import re
from bs4 import BeautifulSoup
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format="[%(asctime)s] %(levelname)-12s|process:%(process)-5s|thread:%(thread)-5s|funcName:%(funcName)s|message:%(message)s",
    handlers=[
        # logging.FileHandler('fileName.log'),
        logging.StreamHandler()
    ])

if __name__ == "__main__":
    # https://transport.lanit.ru/m/table
    # https://transport.lanit.ru/p/table
    # https://transport.lanit.ru/r/table
    response = requests.get('https://transport.lanit.ru/m/table')
    soup = BeautifulSoup(response.text, 'html.parser')
    to_office = soup.select(
        "body > div:nth-child(2) > div > div:nth-child(3) > div:nth-child(1)")
    to_metro = soup.select(
        "body > div:nth-child(2) > div > div:nth-child(3) > div:nth-child(2)")
    to_office_time = re.findall('([0-9]{2}:[0-9]{2})', str(to_office))
    to_metro_time = re.findall('([0-9]{2}:[0-9]{2})', str(to_metro))
