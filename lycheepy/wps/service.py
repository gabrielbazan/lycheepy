from sqlalchemy.orm import joinedload

from pywps import Service, Process

from simplyrestful.database import session

from lycheepy.utils import get_instances_from_package
from lycheepy.models import Chain, Step, StepMatch
from lycheepy.wps.chaining.chain import Chain as ProcessingChain
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


class ProcessesFactory(object):
    processes = {
        process.identifier: process
        for process in get_instances_from_package(PROCESSES_PACKAGE, Process)
    }

    @staticmethod
    def create(identifier):
        return ProcessesFactory.processes.get(identifier)

    @staticmethod
    def create_all():
        return ProcessesFactory.processes


class ChainsFactory(object):
    chains = {}

    @staticmethod
    def _load_instances():
        chains_models = session.query(Chain).options(
            joinedload(Chain.steps).joinedload(Step.matches).joinedload(StepMatch.step),
            joinedload(Chain.steps).joinedload(Step.chain)
        ).all()
        for chain_model in chains_models:
            chain = ProcessingChain(chain_model, ProcessesFactory.create_all())
            ChainsFactory.chains[chain_model.identifier] = chain

    @staticmethod
    def create_all():
        if not ChainsFactory.chains:
            ChainsFactory._load_instances()
        return ChainsFactory.chains

    @staticmethod
    def create(identifier):
        return ChainsFactory.create_all().get(identifier)
