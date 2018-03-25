from validators.executable import ExecutableValidator
from simplyrestful.exceptions import Conflict
from models import Format, DataType


class ProcessValidator(ExecutableValidator):

    def validate(self, data, instance=None):
        super(ProcessValidator, self).validate(data, instance=instance)
        self._validate_parameters(data.get('inputs'))
        self._validate_parameters(data.get('outputs'))

    @staticmethod
    def _validate_parameters(parameters):
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
