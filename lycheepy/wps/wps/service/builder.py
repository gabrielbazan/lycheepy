from pywps import Service
from adapter import ExecutableAdapterBuilder


class ServiceBuilder(object):

    def __init__(self, executor, configuration_file):
        self.service = Service(cfgfiles=[configuration_file])
        self.executor = executor

    def add(self, process):
        self.service.processes[process.identifier] = process
        return self

    def extend(self, processes):
        self.service.processes.update(processes)
        return self

    def add_executables(self):
        self.extend(
            {
                executable.get('identifier'): ExecutableAdapterBuilder(executable).build()
                for executable in self.executor.get_executables()
            }
        )
        return self

    def build(self):
        return self.service
