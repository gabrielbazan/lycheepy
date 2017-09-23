from celery import Celery

import json
import uuid

from pywps.app.WPSRequest import WPSRequest
from lycheepy.wps.chaining.distribution.serialization import OutputsSerializer

from lycheepy.wps.chaining.distribution import broker_configuration

app = Celery('lycheepy')

app.config_from_object(broker_configuration)


@app.task
def run_process(process, wps_request_json):
    from lycheepy.wps.service import ServiceBuilder

    service = ServiceBuilder().add_process(process['module'], process['class']).build()

    request = WPSRequest()
    request.json = json.loads(wps_request_json)
    request.status = 'false'

    identifier = service.processes.keys()[0]

    # Use chain's execution UUID
    response = service.processes[identifier].execute(
        request,
        uuid.uuid1()
    )

    return OutputsSerializer.to_json(response.outputs)
