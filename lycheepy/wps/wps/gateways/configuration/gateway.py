from requests import get


READ_SUCCESS_CODE = 200


class ConfigurationGateway(object):

    def __init__(self, url):
        self.url = url

    @property
    def uri(self):
        return '{}/executables'.format(self.url)

    def get_executables_metadata(self):
        response = get(self.uri)
        return response.json() if response.status_code == READ_SUCCESS_CODE else []
