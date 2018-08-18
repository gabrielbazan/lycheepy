from pywps import ComplexInput, Format, ComplexOutput, Process
from pywps.app.Common import Metadata


class L1B(Process):
    def __init__(self):
        inputs = [
            ComplexInput('SCS', '', [Format('application/x-ogc-wcs; version=2.0')])
        ]

        outputs = [
            ComplexOutput('MDG', '', [Format('application/x-ogc-wcs; version=2.0')])
        ]

        super(L1B, self).__init__(
            self._handler,
            identifier='L1B',
            version='None',
            title='L1B Processor',
            abstract='',
            profile='',
            metadata=[Metadata('Level 1B'), Metadata('Processor')],
            inputs=inputs,
            outputs=outputs,
            store_supported=True,
            status_supported=True
        )

    def _handler(self, request, response):
        response.outputs['MDG'].file = request.inputs['SCS'][0].file
        response.outputs['MDG'].as_reference = True
        return response
