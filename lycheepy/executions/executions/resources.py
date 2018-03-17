from simplyrestful.resources import Resource
from serializers import ExecutionSerializer


class ExecutionResource(Resource):
    endpoint = 'executions'
    serializer = ExecutionSerializer
