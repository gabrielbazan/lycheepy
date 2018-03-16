from pywps import ComplexInput, Format, ComplexOutput, Process, LiteralInput
from pywps.app.Common import Metadata


class L0(Process):
    def __init__(self):
        inputs = [
            LiteralInput('crude', 'Crude Data', data_type='string')
        ]

        outputs = [
            ComplexOutput('RAW', '', [Format('application/x-ogc-wcs; version=2.0')])
        ]

        super(L0, self).__init__(
            self._handler,
            identifier='L0',
            version='None',
            title='L0 Processor',
            abstract='',
            profile='',
            metadata=[Metadata('Level L0'), Metadata('Processor')],
            inputs=inputs,
            outputs=outputs,
            store_supported=True,
            status_supported=True
        )

    def _handler(self, request, response):

        response.outputs['RAW'].file = '/home/gpc/src/lycheepy/tests/cosmo-skymed/CSKS2_GEC_B_HI_16_HH_RA_SF_20130301045754_20130301045801.S01.QLK.tif'
        response.outputs['RAW'].as_reference = True

        return response
