from chaining.publication import Repositories


WPS_CONFIG_FILE = '/root/wps/pywps.cfg'

PROCESSES_PACKAGE = 'processes'

PROCESS_EXECUTION_TIMEOUT = 30

REPOSITORIES = {
    Repositories.GEO_SERVER: [
        {
            'protocol': 'http',
            'host': 'repository',
            'port': 8080
        }
    ]
}

CHAINS_CONFIGURATION_URI = 'http://configuration/chains'
