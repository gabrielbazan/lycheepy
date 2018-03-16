from pywps import ComplexInput, Format, ComplexOutput, Process, LiteralInput
from pywps.app.Common import Metadata


class L1A(Process):
    def __init__(self):
        inputs = [
            LiteralInput('RAW', 'RAW Data', data_type='string')
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

        response.outputs['SCS'].file = '/root/workdir/CSKS2_GEC_B_HI_16_HH_RA_SF_20130301045754_20130301045801.S01.QLK.tif'
        response.outputs['SCS'].as_reference = True

        return response
