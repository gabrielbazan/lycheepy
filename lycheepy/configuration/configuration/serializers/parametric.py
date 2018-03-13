from simplyrestful.serializers import Serializer
from models import Format, DataType


class FormatSerializer(Serializer):
    model = Format


class DataTypeSerializer(Serializer):
    model = DataType
