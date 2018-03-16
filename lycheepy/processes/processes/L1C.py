from pywps import ComplexInput, Format, ComplexOutput, Process, LiteralInput
from pywps.app.Common import Metadata


class L1C(Process):
    def __init__(self):
        inputs = [
            ComplexInput('MDG', '', [Format('application/x-ogc-wcs; version=2.0')])
        ]

        outputs = [
            ComplexOutput('GEC', '', [Format('application/x-ogc-wcs; version=2.0')])
        ]

        super(L1C, self).__init__(
            self._handler,
            identifier='L1C',
            version='None',
            title='L1C Processor',
            abstract='',
            profile='',
            metadata=[Metadata('Level 1C'), Metadata('Processor')],
            inputs=inputs,
            outputs=outputs,
            store_supported=True,
            status_supported=True
        )

    def _handler(self, request, response):

        response.outputs['GEC'].file = '/home/gpc/src/lycheepy/tests/cosmo-skymed/CSKS2_GEC_B_HI_16_HH_RA_SF_20130301045754_20130301045801.S01.QLK.tif'
        response.outputs['GEC'].as_reference = True

        return response
