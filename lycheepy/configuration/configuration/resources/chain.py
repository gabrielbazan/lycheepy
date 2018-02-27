from simplyrestful.resources import Resource
from serializers import ChainSerializer


class ChainResource(Resource):
    endpoint = 'chains'
    serializer = ChainSerializer
