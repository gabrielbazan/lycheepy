from simplyrestful.resources import Resource
from serializers import *


class ProcessResource(Resource):
    endpoint = 'processes'
    serializer = ProcessSerializer


class ChainResource(Resource):
    endpoint = 'chains'
    serializer = ChainSerializer


class ExecutionResource(Resource):
    endpoint = 'executions'
    serializer = ExecutionSerializer
    read_only = True  # TODO: Implement in simplyrestful
