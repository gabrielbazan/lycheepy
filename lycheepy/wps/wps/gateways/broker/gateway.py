from celery import Celery,group


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

        @self.app.task(name='run_chain_process')
        def run_chain_process(identifier, wps_request_json, products, chain_identifier, execution_id):
            pass

        self.run_process = run_process
        self.run_chain_process = run_chain_process

    def run_processes(self, processes):
        return group(
            [
                self.run_chain_process.s(
                    process,
                    data['request'],
                    data['products'],
                    data['chain_identifier'],
                    data['execution_id']
                )
                for process, data in processes.iteritems()
            ]
        ).apply_async()
