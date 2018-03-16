from pywps import Service
from gateways.configuration import ConfigurationGateway
from gateways.broker.process_metadata_builder import ProcessMetadataBuilder


class ServiceBuilder(object):

    def __init__(self, configuration_file, configuration_url):
        self.service = Service(cfgfiles=[configuration_file])
        self.configuration = ConfigurationGateway(configuration_url)

    def add(self, process):
        self.service.processes[process.identifier] = process
        return self

    def extend(self, processes):
        self.service.processes.update(processes)
        return self

    def add_executables(self):
        self.extend(
            {
                executable.get('identifier'): ProcessMetadataBuilder(executable).build()
                for executable in self.configuration.get_executables_metadata()
            }
        )
        return self

    def build(self):
        return self.service
