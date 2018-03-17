FROM python:2

ADD requirements.txt /root/
ADD executions/ /root/executions/
ADD wait-service.sh /root/

WORKDIR /root/

RUN virtualenv venv
RUN /root/venv/bin/pip install -r requirements.txt

CMD ./wait-service.sh executions-persistence 5432 && \
    /root/venv/bin/python /root/executions/models.py && \
    /root/venv/bin/python /root/executions/parametric.py && \
    cd /root/executions; /root/venv/bin/gunicorn -b 0.0.0.0:80 wsgi
