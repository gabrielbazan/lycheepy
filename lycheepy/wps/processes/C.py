from pywps import Process, LiteralInput, LiteralOutput


class C(Process):

    def __init__(self):
        inputs = [LiteralInput('number1', 'number1', data_type="integer")]
        outputs = [LiteralOutput('plus', 'plus', data_type="integer")]

        super(C, self).__init__(
            self._handler,
            identifier='C',
            version='0.4',
            title="process",
            abstract="process",
            profile='',
            inputs=inputs,
            outputs=outputs,
            store_supported=True,
            status_supported=True
        )

    def _handler(self, request, response):
        response.outputs['plus'].data = request.inputs['number1'][0].data + 1
        return response
