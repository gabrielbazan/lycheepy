from sqlalchemy.orm import joinedload

from pywps import Service, Process

from simplyrestful.database import session

from lycheepy.utils import get_instances_from_package
from lycheepy.models import Chain, Step, StepMatch
from lycheepy.settings import WPS_CONFIG_FILE, PROCESSES_PACKAGE


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
    _processes = {}

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
    _chains = {}

    @staticmethod
    def _load_instances():
        from lycheepy.wps.chaining.chain_builder import ChainBuilder
        models = session.query(Chain).options(
            joinedload(Chain.steps).joinedload(Step.matches).joinedload(StepMatch.step),
            joinedload(Chain.steps).joinedload(Step.chain)
        ).all()
        for model in models:
            ChainsGateway._chains[model.identifier] = ChainBuilder(model).build()

    @staticmethod
    def all():
        if not ChainsGateway._chains:
            ChainsGateway._load_instances()
        return ChainsGateway._chains

    @staticmethod
    def get(identifier):
        return ChainsGateway.all().get(identifier)
