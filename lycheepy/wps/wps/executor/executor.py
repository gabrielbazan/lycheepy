import json
from gateways.broker import BrokerGateway
from gateways.executions import ExecutionsGateway
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
        self.executions = ExecutionsGateway(EXECUTIONS_URL)

    def execute_process(self, identifier, request):
        result = self.broker.run_process.delay(identifier, json.loads(request.json)).get(
            timeout=PROCESS_EXECUTION_TIMEOUT
        )
        return result.get('outputs')

    def execute_chain(self, model, request, execution_id):
        self.executions.start(model.get('identifier'), str(execution_id))
        try:
            outputs = ChainBuilder(model).build().execute(self.broker, request, execution_id)
            self.executions.success(str(execution_id))
            return outputs
        except Exception as e:
            self.executions.failure(str(execution_id), str(e))
            raise
