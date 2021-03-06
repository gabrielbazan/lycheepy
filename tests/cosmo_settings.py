from os.path import join
from settings import PROCESSES_DIRECTORY


PROCESSES_DIRECTORY = join(PROCESSES_DIRECTORY, 'cosmo')


PROCESSES = [
    dict(
        specification=dict(
            identifier='L0',
            title='L0 Processor',
            abstract='The L0 processor generates the RAW product',
            version='0.1',
            metadata=['Level 0', 'Processor'],
            inputs=[
                dict(
                    identifier='crude',
                    title='crude',
                    abstract='Crude data',
                    format='GEOTIFF'
                )
            ],
            outputs=[
                dict(
                    identifier='RAW',
                    title='RAW output',
                    abstract='RAW product',
                    format='GEOTIFF'
                )
            ]
        ),
        file=join(PROCESSES_DIRECTORY, 'L0.py')
    ),
    dict(
        specification=dict(
            identifier='L1A',
            title='Level 1A Process',
            abstract='The level 1A processor generates the SCS product',
            version='0.1',
            metadata=['L1A', 'Processor'],
            inputs=[
                dict(
                    identifier='RAW',
                    title='RAW data',
                    abstract='RAW product',
                    format='GEOTIFF'
                )
            ],
            outputs=[
                dict(
                    identifier='SCS',
                    title='SCS Product',
                    abstract='SCS Product',
                    format='GEOTIFF'
                )
            ]
        ),
        file=join(PROCESSES_DIRECTORY, 'L1A.py')
    ),
    dict(
        specification=dict(
            identifier='L1B',
            title='L1B Processor',
            abstract='The Level 1B processor generates the MDG product',
            version='1.0',
            metadata=['L1B', 'Processor'],
            inputs=[
                dict(
                    identifier='SCS',
                    title='SCS Product',
                    abstract='SCS Product',
                    format='GEOTIFF'
                )
            ],
            outputs=[
                dict(
                    identifier='MDG',
                    title='MDG Product',
                    abstract='MDG Product',
                    format='GEOTIFF'
                )
            ]
        ),
        file=join(PROCESSES_DIRECTORY, 'L1B.py')
    ),
    dict(
        specification=dict(
            identifier='L1C',
            title='L1C Processor',
            abstract='The level 1C Processor generates the GEC product',
            version='1.0',
            metadata=['L1C', 'Processor'],
            inputs=[
                dict(
                    identifier='MDG',
                    title='MDG Product',
                    abstract='MDG Product',
                    format='GEOTIFF'
                )
            ],
            outputs=[
                dict(
                    identifier='GEC',
                    title='GEC Product',
                    abstract='GEC Product',
                    format='GEOTIFF'
                )
            ]
        ),
        file=join(PROCESSES_DIRECTORY, 'L1C.py')
    ),
    dict(
        specification=dict(
            identifier='L1D',
            title='L1D Processor',
            abstract='The level 1D Processor generates the GTC product',
            version='0.1',
            metadata=['Level', '1D', 'Processor'],
            inputs=[
                dict(
                    identifier='MDG',
                    title='MDG Product',
                    abstract='MDG Product',
                    format='GEOTIFF'
                )
            ],
            outputs=[
                dict(
                    identifier='GTC',
                    title='GTC Product',
                    abstract='GTC Product',
                    format='GEOTIFF'
                )
            ]
        ),
        file=join(PROCESSES_DIRECTORY, 'L1D.py')
    )
]


CHAIN = dict(
    identifier='Cosmo Skymed',
    title='CSK Standard Processing Model',
    abstract='Takes as input the acquisition from the satellite, and generates all the Standard SAR Products',
    version='0.1',
    metadata=['CSK', 'Mission', 'Chain'],
    steps=[
        dict(after='L1A', before='L0'),
        dict(after='L1B', before='L1A'),
        dict(after='L1C', before='L1B'),
        dict(after='L1D', before='L1B')
    ],
    publish=dict(
        L1D=['GTC'],
        L0=['RAW'],
        L1A=['SCS'],
        L1B=['MDG'],
        L1C=['GEC']
    )
)
