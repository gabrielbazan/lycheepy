from simplyrestful.resources import Resource
from serializers import *


class ProcessResource(Resource):
    endpoint = 'processes'
    serializer = ProcessSerializer


class ChainResource(Resource):
    endpoint = 'chains'
    serializer = ChainSerializer
