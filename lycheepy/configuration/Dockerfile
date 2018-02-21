FROM python:2

ADD requirements.txt /root/
ADD configuration/ /root/configuration/
ADD configuration.conf /etc/init/

WORKDIR /root/

RUN virtualenv venv

RUN /root/venv/bin/pip install -r requirements.txt

RUN /root/venv/bin/python /root/configuration/models.py

CMD start configuration
