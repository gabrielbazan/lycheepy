from os.path import join, dirname


DIR = dirname(__file__)


HOST = 'http://localhost'
CONFIGURATION_URL = '{}/configuration'.format(HOST)
PROCESSES_URL = '{}/processes'.format(CONFIGURATION_URL)
CHAINS_URL = '{}/chains'.format(CONFIGURATION_URL)
WPS_URL = '{}/wps/'.format(HOST)
EXECUTIONS_URL = '{}/executions/executions'.format(HOST)
CSW_URL = '{}/repository/geoserver/csw'.format(HOST)

WCS_RASTER = 'http://repository:8080/geoserver/ows?service=WCS&amp;version=2.0.0&amp;request=GetCoverage&amp;coverageId=nurc:Img_Sample&amp;format=image/tiff'


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
