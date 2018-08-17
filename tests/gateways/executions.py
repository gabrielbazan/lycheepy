from requests import get


class ExecutionsGateway(object):

    def __init__(self, uri):
        self.uri = uri

    def get(self, execution_id):
        response = get('{}?execution_id__eq={}'.format(self.uri, execution_id))
        assert response.status_code == 200, 'Failed to query execution'
        results = response.json().get('results')
        assert results, 'Execution is not published'
        return results[0]
