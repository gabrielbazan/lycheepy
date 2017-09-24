import uuid

from celery import Celery, group

from pywps.app.WPSRequest import WPSRequest

from lycheepy.wps.chaining.distribution import broker_configuration
from lycheepy.wps.chaining.distribution.serialization import OutputsSerializer


app = Celery('lycheepy')

app.config_from_object(broker_configuration)


def run_processes(processes):
    return group(
        [
            run_process.s(process, request)
            for process, request in processes.iteritems()
        ]
    ).apply_async()


@app.task
def run_process(process, wps_request_json):
    from lycheepy.wps.service import ServiceBuilder, ProcessesGateway

    service = ServiceBuilder().add(ProcessesGateway.get(process)).build()

    request = WPSRequest()
    request.json = wps_request_json
    request.status = 'false'

    identifier = service.processes.keys()[0]

    # TODO: Use chain's execution UUID?
    response = service.processes[identifier].execute(
        request,
        uuid.uuid1()
    )

    return dict(
        process=identifier,
        output=OutputsSerializer.to_json(response.outputs)
    )
