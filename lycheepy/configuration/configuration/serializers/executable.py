from simplyrestful.serializers import Serializer
from chain import ChainSerializer
from process import ProcessSerializer
from models import Process, Chain


class ExecutableSerializer(Serializer):
    process_serializer = ProcessSerializer()
    chain_serializer = ChainSerializer()

    def __init__(self):
        pass

    def list(self, filtering):
        processes = [
            ExecutableSerializer.process_serializer.serialize(process)
            for process in Process.query.all()
        ]

        chains = [
            ExecutableSerializer.chain_serializer.serialize(chain)
            for chain in Chain.query.all()
        ]

        return processes + chains

    def create(self, data):
        pass

    def update(self, identifier, data):
        pass

    def read(self, identifier):
        pass
