from os.path import join, dirname


DIR = dirname(__file__)


HOST = 'http://localhost'
CONFIGURATION_URL = '{}/configuration'.format(HOST)
PROCESSES_URL = '{}/processes'.format(CONFIGURATION_URL)
CHAINS_URL = '{}/chains'.format(CONFIGURATION_URL)
WPS_URL = '{}/wps/'.format(HOST)
EXECUTIONS_URL = '{}/executions/executions'.format(HOST)

RASTER_DOWNLOAD_URL = 'https://www.mapbox.com/help/data/landsat.tif'


PROCESS_SPECIFICATION = dict(
    identifier='Process',
    title='Process title',
    abstract='A process',
    version='0.1.2',
    metadata=['Test', 'Process'],
    inputs=[
        dict(
            identifier='a',
            title='A',
            abstract='An input',
            format='GEOTIFF'
        )
    ],
    outputs=[
        dict(
            identifier='b',
            title='B',
            abstract='An output',
            format='GEOTIFF'
        )
    ]
)

PROCESSES_DIRECTORY = join(DIR, 'processes')
PROCESS_FILE = join(PROCESSES_DIRECTORY, 'process.py')
