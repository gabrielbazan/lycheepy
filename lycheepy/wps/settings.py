HOST = '0.0.0.0'
PORT = 5000
DEBUG = True

WPS_CONFIG_FILE = '/home/gpc/src/lycheepy/lycheepy/wps/pywps.cfg'

PROCESSES_PACKAGE = 'processes'

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
