from celery import Celery, Task

import json
import uuid

from pywps.app.WPSRequest import WPSRequest
from lycheepy.wps.chaining.distribution.serialization import OutputsSerializer


app = Celery('lycheepy')

app.config_from_object('lycheepy.wps.chaining.distribution.broker_configuration')


class ProcessCaller(Task):

    def run(self, process, wps_request_json):
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
