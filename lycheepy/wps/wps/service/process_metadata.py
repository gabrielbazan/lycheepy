from pywps import Process


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
        return response
