from pywps import Process
from gateways.broker import BrokerGateway
from gateways.broker.serialization import OutputsDeserializer
from settings import *


class ProcessMetadata(Process):

    def __init__(self, inputs, outputs, identifier, version, title, abstract):
        super(ProcessMetadata, self).__init__(
            self._handle,
            identifier=identifier,
            version=version,
            title=title,
            abstract=abstract,
            profile='',
            inputs=inputs,
            outputs=outputs,
            store_supported=True,
            status_supported=True
        )

    def _handle(self, request, response):

        broker = BrokerGateway(
            BROKER_HOST,
            BROKER_PROTOCOL,
            BROKER_USERNAME,
            BROKER_APPLICATION_NAME,
            BROKER_TASK_NAME
        )

        promise = broker.run_process.delay(self.identifier, request.json)

        result = promise.get(timeout=PROCESS_EXECUTION_TIMEOUT)

        outputs = result.get('outputs')

        for output in self.outputs:
            output_identifier = output.identifier
            OutputsDeserializer.add_data(
                outputs.get(output_identifier)[0],  # TODO: Handle outputs with multiple occurrences
                response.outputs.get(output_identifier)
            )

        return response
