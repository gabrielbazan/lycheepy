FROM python:2

ADD requirements.txt /root/
ADD configuration/ /root/configuration/
ADD configuration.conf /etc/init/
ADD wait-for-persistence.sh /root/

WORKDIR /root/

RUN virtualenv venv
RUN /root/venv/bin/pip install -r requirements.txt

CMD ./wait-for-persistence.sh; /root/venv/bin/python /root/configuration/models.py; start configuration
