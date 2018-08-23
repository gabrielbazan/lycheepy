from pywps import Process
from executor import Executor
from gateways.broker.serialization import OutputsDeserializer


class ExecutableAdapter(Process):

    def __init__(self, inputs, outputs, identifier, version, title, abstract, model, is_chain=False):
        super(ExecutableAdapter, self).__init__(
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
        self.model = model
        self.is_chain = is_chain

    def _handle(self, request, response):
        executor = Executor()

        if self.is_chain:
            outputs = executor.execute_chain(self.model, request, self.uuid)
        else:
            outputs = executor.execute_process(self.identifier, request)

        for output in self.outputs:
            output_identifier = output.identifier
            for result_output in outputs.get(output_identifier):
                OutputsDeserializer.add_data(result_output, response.outputs.get(output_identifier))

        return response

    def clean(self):
        pass
