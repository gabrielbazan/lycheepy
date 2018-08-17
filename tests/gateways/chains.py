from requests import get, post, put, delete


class ChainsGateway(object):

    def __init__(self, uri):
        self.uri = uri

    def list(self):
        return get(self.uri)

    def create(self, specification):
        return post(self.uri, json=specification)

    def get(self, identifier):
        return get('{}/{}'.format(self.uri, identifier))

    def update(self, identifier, specification, process_file):
        pass

    def delete(self, identifier):
        return delete('{}/{}'.format(self.uri, identifier))

    def exists(self, identifier):
        response = get('{}?identifier__eq={}'.format(self.uri, identifier))
        assert response.status_code == 200, 'Failed to query chain'
        return response.json().get('results')
