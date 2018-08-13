FROM python:2

WORKDIR /root/

ADD requirements.txt /root/

RUN virtualenv venv
RUN /root/venv/bin/pip install -r requirements.txt

RUN /root/venv/bin/pip install -e git+https://github.com/geopython/pywps.git@master#egg=pywps-dev
RUN /root/venv/bin/pip install flufl.enum

ADD wps/ /root/wps/
ADD wait-service.sh /root/

RUN mkdir /root/outputs
RUN mkdir /root/workdir
RUN mkdir /root/logs

CMD ./wait-service.sh configuration 80 && \
    cd /root/wps; /root/venv/bin/gunicorn -b 0.0.0.0:80 wsgi
