import uuid
from celery import Celery
from pywps import Service
from pywps.app.WPSRequest import WPSRequest
from settings import *
import configuration
from serialization import OutputsSerializer
from gateways.repository import RepositoryFactory
from gateways.processes import ProcessesGateway


app = Celery(BROKER_APPLICATION_NAME)

app.config_from_object(configuration)


@app.task(name=BROKER_TASK_NAME)
def run_process(identifier, wps_request_json):

    processes = ProcessesGateway(
        PROCESSES_GATEWAY_HOST,
        PROCESSES_GATEWAY_USER,
        PROCESSES_GATEWAY_PASS,
        PROCESSES_GATEWAY_TIMEOUT,
        PROCESSES_GATEWAY_DIRECTORY
    )

    print identifier
    print wps_request_json

    i = processes.get_instance(identifier, LOCAL_PROCESSES_REPOSITORY)

    print i

    service = Service([i], 'the_cfg_file')

    request = WPSRequest()
    request.json = wps_request_json
    request.status = 'false'

    response = service.processes.get(identifier).execute(
        request,
        uuid.uuid1()
    )

    outputs = OutputsSerializer.to_json(response.outputs)

    return dict(process=identifier, outputs=outputs)


@app.task(name='run_chain_process')
def run_chain_process(identifier, wps_request_json, products, chain_identifier, execution_id):
    outputs = run_process(identifier, wps_request_json).get('outputs')
    publish(products, identifier, outputs, chain_identifier, execution_id)
    return dict(process=identifier, outputs=outputs)


def publish(products, process, outputs, chain_identifier, execution_id):
    print 'products: ', products
    print 'outputs: ', outputs
    for output_identifier, output in outputs.iteritems():
        print output_identifier, output
        if output_identifier in products:
            product_identifier = '{}:{}:{}:{}'.format(
                chain_identifier, execution_id, process, output_identifier
            )
            print product_identifier
            for occurrence in output:
                print occurrence
                for kind, repositories in REPOSITORIES.iteritems():
                    for config in repositories:
                        RepositoryFactory.create(kind, config).publish(product_identifier, occurrence.get('file'))
