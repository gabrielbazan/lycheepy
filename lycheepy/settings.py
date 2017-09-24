DATABASE = 'postgresql://postgres:postgres@localhost/lycheepy'
HOST = '0.0.0.0'
PORT = 5000
DEBUG = True

DEFAULT_PAGE_SIZE = 10
MAX_PAGE_SIZE = 100

WPS_CONFIG_FILE = '/home/gpc/src/lycheepy/lycheepy/wps/pywps.cfg'

PROCESSES_PACKAGE = 'lycheepy.wps.processes'

PROCESS_EXECUTION_TIMEOUT = 30

REPOSITORIES = {
    'GEO_SERVER': [
        {
            'protocol': 'http',
            'host': 'gpc',
            'port': 8080
        }
    ]
}
