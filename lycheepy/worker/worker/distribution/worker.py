import logging
from uuid import uuid1
from json import dumps
from celery import Celery
from pywps import Service
from pywps.app.WPSRequest import WPSRequest
from settings import *
from serialization import OutputsSerializer
from gateways.repository import RepositoryFactory
from gateways.processes import ProcessesGateway


broker_url = '{}://{}:{}@{}:{}//'.format(BROKER_PROTOCOL, BROKER_USERNAME, BROKER_PASSWORD, BROKER_HOST, BROKER_PORT)

app = Celery(BROKER_APPLICATION_NAME, broker=broker_url, backend=broker_url)


@app.task(name=BROKER_PROCESS_EXECUTION_TASK_NAME)
def run_process(identifier, wps_request_json):

    processes = ProcessesGateway(
        PROCESSES_GATEWAY_HOST,
        PROCESSES_GATEWAY_USER,
        PROCESSES_GATEWAY_PASS,
        PROCESSES_GATEWAY_TIMEOUT,
        PROCESSES_GATEWAY_DIRECTORY
    )

    request = WPSRequest()
    request.json = wps_request_json
    request.status = 'false'

    logging.info('WPS request: {}'.format(dumps(wps_request_json)))

    with processes.get_process_context(identifier, LOCAL_PROCESSES_REPOSITORY) as process_context:
        service = Service([process_context.get_process_instance()], CONFIGURATION_FILE)
        response = service.processes.get(identifier).execute(request, uuid1())
        outputs = OutputsSerializer.to_json(response.outputs)

    logging.info('Process outputs: {}'.format(dumps(outputs)))

    return dict(process=identifier, outputs=outputs)


@app.task(name=BROKER_CHAIN_PROCESS_EXECUTION_TASK_NAME)
def run_chain_process(identifier, wps_request_json, products, chain_identifier, execution_id):
    outputs = run_process(identifier, wps_request_json).get('outputs')
    publish(products, identifier, outputs, chain_identifier, execution_id)
    return dict(process=identifier, outputs=outputs)


def publish(products, process, outputs, chain_identifier, execution_id):
    for output_identifier, output in outputs.iteritems():
        if output_identifier in products:
            product_identifier = '{}:{}:{}:{}'.format(
                chain_identifier, execution_id, process, output_identifier
            )
            for occurrence in output:
                for kind, repositories in REPOSITORIES.iteritems():
                    for config in repositories:
                        RepositoryFactory.create(kind, config).publish(product_identifier, occurrence.get('file'))
