from pywps import ComplexInput, Format, ComplexOutput, Process, LiteralInput
from pywps.app.Common import Metadata


class L0(Process):
    def __init__(self):
        inputs = [
            LiteralInput('crude', 'Crude Data', data_type='string')
        ]

        outputs = [
            ComplexOutput('RAW', 'RAW output', [Format('image/tiff; subtype=geotiff')])
        ]

        super(L0, self).__init__(
            self._handler,
            identifier='L0',
            version='0.1',
            title='L0 Processor',
            abstract='L0 Processor, which generates the RAW product',
            profile='',
            metadata=[Metadata('Level L0'), Metadata('Processor')],
            inputs=inputs,
            outputs=outputs,
            store_supported=True,
            status_supported=True
        )

    def _handler(self, request, response):
        response.outputs['RAW'].file = '/root/workdir/CSKS2_GEC_B_HI_16_HH_RA_SF_20130301045754_20130301045801.S01.QLK.tif'
        response.outputs['RAW'].as_reference = True
        return response
