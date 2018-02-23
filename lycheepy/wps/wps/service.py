from pywps import Service, Process
from utils import get_instances_from_package
from settings import WPS_CONFIG_FILE, PROCESSES_PACKAGE, CHAINS_CONFIGURATION_URI
from requests import get


class ServiceBuilder(object):
    def __init__(self):
        self.service = Service(cfgfiles=[WPS_CONFIG_FILE])

    def add(self, process):
        self.service.processes[process.identifier] = process
        return self

    def extend(self, processes):
        self.service.processes.update(processes)
        return self

    def build(self):
        return self.service


class ProcessesGateway(object):
    _processes = dict()

    @staticmethod
    def _load_instances():
        ProcessesGateway._processes = {
            process.identifier: process
            for process in get_instances_from_package(PROCESSES_PACKAGE, Process)
        }

    @staticmethod
    def all():
        if not ProcessesGateway._processes:
            ProcessesGateway._load_instances()
        return ProcessesGateway._processes

    @staticmethod
    def get(identifier):
        return ProcessesGateway.all().get(identifier)


class ChainsGateway(object):
    _chains = dict()

    @staticmethod
    def _load_instances():
        from chaining.chain_builder import ChainBuilder
        ChainsGateway._chains = {
            chain.get('identifier'): ChainBuilder(chain).build()
            for chain in ChainsGateway._retrieve_chains()
        }

    @staticmethod
    def _retrieve_chains():
        return get(CHAINS_CONFIGURATION_URI).json().get('results')

    @staticmethod
    def all():
        if not ChainsGateway._chains:
            ChainsGateway._load_instances()
        return ChainsGateway._chains

    @staticmethod
    def get(identifier):
        return ChainsGateway.all().get(identifier)
