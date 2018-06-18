FROM python:3.6

RUN apt-get update \
    && apt-get install -y \
    mosquitto \
    tmux \
    && apt-get clean

WORKDIR /app

COPY ./requirements.txt ./requirements.txt

RUN pip install -r requirements.txt

COPY . .

CMD ["./run.sh", "--log", "debug", "--rpi-mock"]
