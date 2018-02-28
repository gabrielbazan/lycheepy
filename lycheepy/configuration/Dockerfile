FROM python:2

ADD requirements.txt /root/
ADD configuration/ /root/configuration/
ADD wait-service.sh /root/

WORKDIR /root/

RUN virtualenv venv
RUN /root/venv/bin/pip install -r requirements.txt

CMD ./wait-service.sh persistence 5432; \
    /root/venv/bin/python /root/configuration/models.py; \
    /root/venv/bin/python /root/configuration/parametric.py; \
    cd /root/configuration; /root/venv/bin/gunicorn -b 0.0.0.0:80 wsgi
