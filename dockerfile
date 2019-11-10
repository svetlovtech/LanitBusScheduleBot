FROM python:latest

WORKDIR /home/lanit_bot

COPY resources resources
COPY requirements.txt requirements.txt
COPY main.py main.py
COPY bus_schedule.py bus_schedule.py
COPY bus_schedule.py bus_schedule.py
COPY settings.py settings.py

RUN ["apt-get", "update", "-y"]
RUN ["apt-get", "upgrade", "-y"]
RUN ["pip", "install", "-r", "requirements.txt"]

ENTRYPOINT ["python", "main.py"]
