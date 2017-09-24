import uuid

from celery import Celery, group

from pywps.app.WPSRequest import WPSRequest

from lycheepy.wps.chaining.distribution import broker_configuration
from lycheepy.wps.chaining.distribution.serialization import OutputsSerializer
from lycheepy.wps.chaining.publishing import RepositoryFactory
from lycheepy.settings import REPOSITORIES


app = Celery('lycheepy')

app.config_from_object(broker_configuration)


def run_processes(processes):
    return group(
        [
            run_process.s(
                process,
                data['request'],
                data['products'],
                data['chain_identifier'],
                data['execution_id']
            )
            for process, data in processes.iteritems()
        ]
    ).apply_async()


@app.task
def run_process(process, wps_request_json, products, chain_identifier, execution_id):
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

    outputs = OutputsSerializer.to_json(response.outputs)

    publish(products, process, outputs, chain_identifier, execution_id)

    return dict(process=identifier, output=outputs)


def publish(products, process, outputs, chain_identifier, execution_id):
    mime_types = {
        'application/x-ogc-wcs; version=2.0': 'publish_raster',
        'application/gml+xml': 'publish_features'
    }
    for product in products:
        output = outputs[product][0]  # TODO: Handle multiple occurrences for same output
        mime_type = output['data_format']['mime_type']
        if mime_type in mime_types:
            product_identifier = '{}:{}:{}:{}'.format(
                chain_identifier, execution_id, process, product
            )
            for kind, repositories in REPOSITORIES.iteritems():
                for configuration in repositories:
                    repository = RepositoryFactory.create(kind, configuration)
                    getattr(repository,mime_types[mime_type])(
                        product_identifier,
                        output['file']
                    )
