import importlib

from pywps import Service, Process
from lycheepy.settings import WPS_CONFIG_FILE
from lycheepy.utils import get_instances_from_package
from lycheepy.wps import processes


# from chain.chain import Chain as ProcessingChain
# from lycheepy.api.models import Chain


class ServiceBuilder(object):

    def __init__(self):
        self.service = Service(cfgfiles=[WPS_CONFIG_FILE])

    @staticmethod
    def _get_processes():
        return get_instances_from_package(processes, Process)

    """
    @staticmethod
    def _get_chains(processes_list):
        processes_dict = {p.identifier: p for p in processes_list}
        chains = []
        chains_models = Chain.objects.all()
        for chain_model in chains_models:
            chain = ProcessingChain(chain_model, processes_dict)
            chains.append(chain)
        return chains
    """

    def _add_processes(self, processes_list):
        self.service.processes = {p.identifier: p for p in processes_list}

    def add_process(self, process_module, process_class):
        process = getattr(importlib.import_module(process_module), process_class)()
        self._add_processes([process])
        return self

    def add_processes(self):
        self._add_processes(self._get_processes())
        return self

    """
    def add_chains(self):
        processes_list = self._get_processes()
        chains_list = self._get_chains(processes_list)
        self._add_processes(processes_list + chains_list)
        return self
    """

    def build(self):
        return self.service
