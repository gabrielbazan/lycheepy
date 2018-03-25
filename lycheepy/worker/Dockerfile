FROM python:2

ADD requirements.txt /root/
ADD worker/ /root/worker/
ADD workdir/ /root/workdir/
ADD wait-service.sh /root/

WORKDIR /root/

RUN virtualenv venv
RUN /root/venv/bin/pip install -r requirements.txt

RUN mkdir /root/worker/processes/

CMD ./wait-service.sh broker 5672 && \
    cd /root/worker; /root/venv/bin/celery -A distribution.worker worker --loglevel=info
