from gateways.repository import Repositories


BROKER_APPLICATION_NAME = 'lycheepy'
BROKER_TASK_NAME = 'run_process'

REPOSITORIES = {
    Repositories.GEO_SERVER: [
        {
            'protocol': 'http',
            'host': '192.168.0.225',
            'port': 8080
        }
    ]
}

PROCESSES_GATEWAY_HOST = 'processes'
PROCESSES_GATEWAY_USER = 'lycheepy'
PROCESSES_GATEWAY_PASS = 'lycheepy'
PROCESSES_GATEWAY_TIMEOUT = 30
PROCESSES_GATEWAY_DIRECTORY = 'processes'

LOCAL_PROCESSES_REPOSITORY = '/root/worker/processes'
