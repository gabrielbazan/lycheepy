from requests import get


READ_SUCCESS_CODE = 200


class ConfigurationGateway(object):

    def __init__(self, url):
        self.url = url

    @property
    def chains_uri(self):
        return '{}/chains'.format(self.url)

    @property
    def processes_uri(self):
        return '{}/processes'.format(self.url)

    @staticmethod
    def get(uri, identifier):
        response = get('{}?identifier__eq={}'.format(uri, identifier))
        return response.json() if response.status_code == READ_SUCCESS_CODE else None

    @staticmethod
    def get_list(uri):
        response = get(uri)
        return response.json().get('results') if response.status_code == READ_SUCCESS_CODE else []

    def get_processes(self):
        return self.get_list(self.processes_uri)

    def get_chains(self):
        return self.get_list(self.chains_uri)

    def get_process(self, identifier):
        return self.get(self.processes_uri, identifier=identifier)

    def get_chain(self, identifier):
        return self.get(self.chains_uri, identifier=identifier)

    def get_executable_metadata(self, identifier):
        process = self.get_process(identifier)
        return process if process else self.get_chain(identifier)

    def get_executables_metadata(self):
        return self.get_processes() + self.get_chains()
