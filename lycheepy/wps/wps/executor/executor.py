import json
from gateways.broker import BrokerGateway
from settings import *
from chain_builder import ChainBuilder


class Executor(object):

    def __init__(self):
        self.broker = BrokerGateway(
            BROKER_HOST,
            BROKER_PROTOCOL,
            BROKER_USERNAME,
            BROKER_APPLICATION_NAME,
            BROKER_TASK_NAME
        )

    def execute_process(self, identifier, request):
        result = self.broker.run_process.delay(identifier, json.loads(request.json)).get(
            timeout=PROCESS_EXECUTION_TIMEOUT
        )
        return result.get('outputs')

    def execute_chain(self, model, request, execution_id):
        return ChainBuilder(model).build().execute(self.broker, request, execution_id)
