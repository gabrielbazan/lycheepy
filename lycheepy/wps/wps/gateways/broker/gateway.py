from celery import Celery



class BrokerGateway(object):

    def __init__(self, host, protocol, username, application_name, task_name):
        self.app = Celery(application_name)
        url = '{}://{}@{}//'.format(protocol, username, host)
        self.app.conf.update(
            broker_url=url,
            result_backend=url
        )

        @self.app.task(name=task_name)
        def run_process(identifier, wps_request_json):
            pass

        self.run_process = run_process
