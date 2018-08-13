FROM python:2

WORKDIR /root/

ADD requirements.txt /root/

RUN virtualenv venv
RUN /root/venv/bin/pip install -r requirements.txt

ADD executions/ /root/executions/
ADD wait-service.sh /root/

CMD ./wait-service.sh executions-persistence 5432 && \
    /root/venv/bin/python /root/executions/models.py && \
    /root/venv/bin/python /root/executions/parametric.py && \
    cd /root/executions; /root/venv/bin/gunicorn -b 0.0.0.0:80 wsgi
