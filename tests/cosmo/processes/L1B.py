from pywps import ComplexInput, Format, ComplexOutput, Process, LiteralInput
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

        response.outputs['MDG'].file = '/root/workdir/CSKS2_GEC_B_HI_16_HH_RA_SF_20130301045754_20130301045801.S01.QLK.tif'
        response.outputs['MDG'].as_reference = True

        return response
