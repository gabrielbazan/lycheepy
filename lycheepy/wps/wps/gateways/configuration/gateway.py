from requests import get


READ_SUCCESS_CODE = 200


class ConfigurationGateway(object):

    def __init__(self, url, executables_path, repositories_path, results_key):
        self.url = url
        self.executables_path = executables_path
        self.repositories_path = repositories_path
        self.results_key = results_key

    @staticmethod
    def request(uri, key=None):
        response = get(uri)
        result = []
        if response.status_code == READ_SUCCESS_CODE:
            result = response.json()
            if key:
                result = result.get(key)
        return result

    def build_uri(self, path):
        return '{}/{}'.format(self.url, path)

    @property
    def executables_uri(self):
        return self.build_uri(self.executables_path)

    @property
    def repositories_uri(self):
        return self.build_uri(self.repositories_path)

    def get_executables_metadata(self):
        return ConfigurationGateway.request(self.executables_uri)

    def get_repositories(self):
        return ConfigurationGateway.request(self.repositories_uri, key=self.results_key)
