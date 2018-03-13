from simplyrestful.resources import Resource
from serializers import FormatSerializer, DataTypeSerializer


class FormatResource(Resource):
    endpoint = 'formats'
    serializer = FormatSerializer


class DataTypeResource(Resource):
    endpoint = 'data-types'
    serializer = DataTypeSerializer
