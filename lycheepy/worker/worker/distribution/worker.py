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
def run_chain_process(identifier, wps_request_json, products, chain_identifier, execution_id, repositories):
    outputs = run_process(identifier, wps_request_json).get('outputs')
    publish(products, identifier, outputs, chain_identifier, execution_id, repositories)
    return dict(process=identifier, outputs=outputs)


def publish(products, process, outputs, chain_identifier, execution_id, repositories):
    for output_identifier, output in outputs.iteritems():
        if output_identifier in products:
            publish_output_occurrences(
                process, chain_identifier, execution_id, output, output_identifier, repositories
            )


def publish_output_occurrences(process, chain_identifier, execution_id, output, output_identifier, repositories):
    product_identifier = '{}:{}:{}:{}'.format(
        chain_identifier, execution_id, process, output_identifier
    )
    for occurrence in output:
        for repository in repositories:
            publish_output(occurrence, repository, product_identifier)


def publish_output(occurrence, repository, product_identifier):
    RepositoryFactory.create(repository['type'], repository['configurations']).publish(
        product_identifier,
        occurrence.get('file')
    )
    logging.info('Published "{}" product onto "{}" repository'.format(product_identifier, repository['name']))
