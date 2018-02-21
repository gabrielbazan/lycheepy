FROM ubuntu:16.04

ADD requirements.txt /root/
ADD configuration/ /root/
ADD configuration.conf /etc/init/

RUN apt-get update && apt-get upgrade -y

RUN apt-get install -y python2.7 virtualenv

WORKDIR /root/

RUN virtualenv venv

RUN /root/venv/bin/pip install -r requirements.txt

CMD start configuration
