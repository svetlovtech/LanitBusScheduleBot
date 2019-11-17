from settings import logging
from enum import Enum


class Models(Enum):
    pass


class Locations(Models):
    MARINA_ROSHHA = 'Марьина Роща'
    PLOSHHAD_ILICHA = 'Площадь Ильича'
    RIZHSKAJA = 'Рижская'


class Destinations(Models):
    TO_METRO = 'к метро'
    TO_OFFICE = 'в офис'
