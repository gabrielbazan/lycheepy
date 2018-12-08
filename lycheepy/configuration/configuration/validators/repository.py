from simplyrestful.validators import Validator
from simplyrestful.exceptions import Conflict
from models import RepositoryType


class RepositoryValidator(Validator):

    def validate(self, data, instance=None):
        repository_type = RepositoryValidator.validate_type(data, instance)
        RepositoryValidator.validate_configurations(data, instance, repository_type)

    @staticmethod
    def validate_type(data, instance):
        type_name = data.get('type')

        if instance:
            if type_name and type_name != instance.type.name:
                raise Conflict('The repository type cannot be changed')
            repository_type = instance.type
        else:
            if not type_name:
                raise Conflict('Please, specify the repository type')

            repository_type = RepositoryType.query.filter_by(name=type_name).one_or_none()

            if not repository_type:
                raise Conflict('Invalid repository type')

        return repository_type

    @staticmethod
    def validate_configurations(data, instance, repository_type):
        configurations = data.get('configurations')

        if not instance and not configurations:
            raise Conflict('Please, specify the repository configurations')

        if configurations:
            available = set(RepositoryValidator.get_configurations(repository_type))
            mandatory = set(RepositoryValidator.get_configurations(repository_type, mandatory=True))
            provided = set((name for name, value in configurations.iteritems()))

            non_recognized = provided - available
            if non_recognized:
                raise Conflict('Non recognized configurations: {}'.format(', '.join(non_recognized)))

            missing = mandatory - provided
            if missing:
                raise Conflict(
                    'Missing mandatory configuration: {}'.format(
                        ', '.join(missing)
                    )
                )

    @staticmethod
    def get_configurations(repository_type, mandatory=False):
        return [
            type_setting.setting.name
            for type_setting in repository_type.type_settings
            if not mandatory or type_setting.mandatory
        ]
