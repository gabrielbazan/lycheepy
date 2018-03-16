from pywps import ComplexInput, Format, ComplexOutput, Process, LiteralInput
from pywps.app.Common import Metadata


class L1D(Process):
    def __init__(self):
        inputs = [
            LiteralInput('MDG', 'MDG', data_type='string')
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

        response.outputs['GTC'].file = '/root/workdir/CSKS2_GEC_B_HI_16_HH_RA_SF_20130301045754_20130301045801.S01.QLK.tif'
        response.outputs['GTC'].as_reference = True

        return response
