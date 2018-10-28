import json
from gateways.broker import BrokerGateway
from gateways.executions import ExecutionsGateway
from gateways.configuration import ConfigurationGateway
from settings import *
from chain_builder import ChainBuilder


class Executor(object):

    def __init__(self):
        self.configuration = ConfigurationGateway(CONFIGURATION_URL)
        self.executions = ExecutionsGateway(EXECUTIONS_URL)
        self.broker = BrokerGateway(
            BROKER_HOST,
            BROKER_PORT,
            BROKER_PROTOCOL,
            BROKER_USERNAME,
            BROKER_PASSWORD,
            BROKER_APPLICATION_NAME,
            BROKER_PROCESS_EXECUTION_TASK_NAME,
            BROKER_CHAIN_PROCESS_EXECUTION_TASK_NAME
        )

    def get_executables(self):
        return self.configuration.get_executables_metadata()

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
