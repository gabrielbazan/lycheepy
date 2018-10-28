from simplyrestful.resources import Resource
from serializers import ExecutableSerializer


class ExecutableResource(Resource):
    endpoint = 'executables'
    serializer = ExecutableSerializer
