from pywps import Format, ComplexOutput, Process, ComplexInput
from pywps.app.Common import Metadata


class L1A(Process):
    def __init__(self):
        inputs = [
            ComplexInput('RAW', 'RAW Data', [Format('image/tiff; subtype=geotiff')])
        ]

        outputs = [
            ComplexOutput('SCS', '', [Format('application/x-ogc-wcs; version=2.0')])
        ]

        super(L1A, self).__init__(
            self._handler,
            identifier='L1A',
            version='None',
            title='L1A Processor',
            abstract='',
            profile='',
            metadata=[Metadata('Level 1A'), Metadata('Processor')],
            inputs=inputs,
            outputs=outputs,
            store_supported=True,
            status_supported=True
        )

    def _handler(self, request, response):
        response.outputs['SCS'].file = request.inputs['RAW'][0].file
        response.outputs['SCS'].as_reference = True
        return response
