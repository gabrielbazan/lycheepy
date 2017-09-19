from pywps import Process, LiteralInput, LiteralOutput


class B(Process):

    def __init__(self):

        inputs = [LiteralInput('number', 'number', data_type="integer")]
        outputs = [LiteralOutput('plus', 'plus', data_type="integer")]

        super(B, self).__init__(
            self._handler,
            identifier='B',
            version='0.1',
            title="process",
            abstract="process",
            profile='',
            inputs=inputs,
            outputs=outputs,
            store_supported=True,
            status_supported=True
        )

    def _handler(self, request, response):
        response.outputs['plus'].data = request.inputs['number'][0].data + 1
        return response
