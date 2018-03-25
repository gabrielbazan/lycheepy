from datetime import datetime
from requests import get, post, put


CREATE_SUCCESS_CODE = 201
READ_SUCCESS_CODE = 200


class Statuses(object):
    RUNNING = 'RUNNING'
    SUCCESS = 'SUCCESS'
    FAILURE = 'FAILURE'


class ExecutionsGateway(object):

    def __init__(self, url):
        self.url = url

    @property
    def uri(self):
        return '{}/executions'.format(self.url)

    def start(self, chain_identifier, execution_id):
        return post(
            self.uri,
            json=dict(
                chain_identifier=chain_identifier,
                execution_id=execution_id,
                status=dict(
                    name=Statuses.RUNNING
                )
            )
        ).json()

    def success(self, execution_id):
        return self.finish(execution_id, Statuses.SUCCESS)

    def failure(self, execution_id, reason):
        return self.finish(execution_id, Statuses.FAILURE, reason=reason)

    def finish(self, execution_id, status, reason=''):
        return put(
            '{}/{}'.format(self.uri, self.get(execution_id).get('id')),
            json=dict(
                status=dict(
                    name=status
                ),
                end=datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
                reason=reason
            )
        ).json()

    def get(self, execution_id):
        return get('{}?execution_id={}'.format(self.uri, execution_id)).json().get('results')[0]
