FROM python:2

ADD requirements.txt /root/
ADD wps/ /root/wps/
ADD wait-service.sh /root/

WORKDIR /root/

RUN virtualenv venv
RUN /root/venv/bin/pip install -r requirements.txt

RUN mkdir /root/wps/outputs
RUN mkdir /root/wps/workdir
RUN mkdir /root/wps/logs

CMD ./wait-service.sh configuration 80; \
    cd /root/wps; /root/venv/bin/gunicorn -b 0.0.0.0:80 wsgi
