FROM python:2

ADD requirements.txt /root/
ADD worker/ /root/worker/
ADD workdir/ /root/workdir/
ADD wait-service.sh /root/

WORKDIR /root/

RUN virtualenv venv
RUN /root/venv/bin/pip install -r requirements.txt


#RUN git clone https://github.com/geopython/pywps.git
#RUN cd pywps && /root/venv/bin/python setup.py install && cd -

RUN /root/venv/bin/pip install -e git+https://github.com/geopython/pywps.git@master#egg=pywps-dev
RUN /root/venv/bin/pip install flufl.enum

RUN mkdir /root/worker/processes/

CMD ./wait-service.sh broker 5672 && \
    cd /root/worker; /root/venv/bin/celery -A distribution.worker worker --loglevel=info
