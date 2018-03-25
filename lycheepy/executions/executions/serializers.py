from simplyrestful.serializers import Serializer
from models import ExecutionStatus, Execution


class ExecutionStatusSerializer(Serializer):
    model = ExecutionStatus


class ExecutionSerializer(Serializer):
    model = Execution
    status = ExecutionStatusSerializer
