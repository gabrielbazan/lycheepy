from simplyrestful.validators import Validator
from simplyrestful.exceptions import Conflict
from models import Format, DataType, Chain


class ProcessValidator(Validator):

    def validate(self, data, instance=None):
        ProcessValidator.validate_parameters(data.get('inputs'))
        ProcessValidator.validate_parameters(data.get('outputs'))
        ProcessValidator.validate_unique(data)

    @staticmethod
    def validate_unique(data):
        identifier = data.get('identifier')
        chain = Chain.query.filter_by(identifier=identifier).one_or_none()
        if chain:
            raise Conflict('Already exists a chain with the given identifier')

    @staticmethod
    def validate_parameters(parameters):
        for parameter in parameters:
            data_format = parameter.get('format')
            data_type = parameter.get('dataType')
            both = data_format and data_type
            none = not data_format and not data_type

            if both or none:
                raise Conflict('Process parameters only can have format OR dataType')

            if data_format and not Format.query.filter_by(name=data_format).one_or_none():
                raise Conflict('Invalid format')

            if data_type and not DataType.query.filter_by(name=data_type).one_or_none():
                raise Conflict('Invalid dataType')
