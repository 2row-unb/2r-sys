FROM python:3.6

RUN apt-get update \
    && apt-get install -y tmux wget \
    && apt-get clean \
    && wget http://emqtt.io/static/brokers/emqttd-debian9-v2.3.9_amd64.deb \
    && dpkg -i emqttd-debian9-v2.3.9_amd64.deb \
    && rm -f emqttd-debian9-v2.3.9_amd64.deb

COPY ./emq_sn.conf /etc/emqttd/plugins/emq_sn.conf

WORKDIR /app

COPY ./requirements.txt ./requirements.txt

RUN pip install -r requirements.txt

COPY ./src ./src
COPY ./run.sh ./run.sh
COPY ./tasks.py ./tasks.py

CMD ["sleep", "infinity"]
