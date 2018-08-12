from pywps import Format, ComplexOutput, Process, ComplexInput
from pywps.app.Common import Metadata


class L1D(Process):
    def __init__(self):
        inputs = [
            ComplexInput('MDG', 'MDG', [Format('image/tiff; subtype=geotiff')])
        ]

        outputs = [
            ComplexOutput('GTC', '', [Format('application/x-ogc-wcs; version=2.0')])
        ]

        super(L1D, self).__init__(
            self._handler,
            identifier='L1D',
            version='None',
            title='L1D Processor',
            abstract='',
            profile='',
            metadata=[Metadata('Level L1D'), Metadata('Processor')],
            inputs=inputs,
            outputs=outputs,
            store_supported=True,
            status_supported=True
        )

    def _handler(self, request, response):
        response.outputs['GTC'].file = request.inputs['MDG'][0].file
        response.outputs['GTC'].as_reference = True
        return response
