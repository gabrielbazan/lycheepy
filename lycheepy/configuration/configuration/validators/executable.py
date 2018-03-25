from simplyrestful.validators import Validator
from models import Chain, Process
from simplyrestful.exceptions import Conflict


class ExecutableValidator(Validator):

    def validate(self, data, instance=None):
        self._validate_identifier(data, instance)

    @staticmethod
    def _validate_identifier(data, instance):
        identifier = data.get('identifier')
        process = Process.query.filter_by(identifier=identifier).one_or_none()
        chain = Chain.query.filter_by(identifier=identifier).one_or_none()
        executable = process if process else chain
        if executable and not instance or executable and instance and executable.id != instance.id:
            raise Conflict('A process or chain with the given identifier already exists')
