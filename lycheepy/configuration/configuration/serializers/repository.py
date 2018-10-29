from simplyrestful.serializers import Serializer
from models import Repository, RepositoryType, RepositoryConfiguration, RepositoryTypeSetting, RepositorySetting
from validators import RepositoryValidator


class RepositorySerializer(Serializer):
    model = Repository
    validators = [RepositoryValidator]

    def serialize(self, instance):
        serialized = super(RepositorySerializer, self).serialize(instance)

        del serialized['type_id']

        serialized.update(
            type=instance.type.name,
            configurations={
                configuration.type_setting.setting.name: configuration.value
                for configuration in instance.configurations
            },
            availableConfigurations=RepositorySerializer.get_configurations(instance),
            mandatoryConfigurations=RepositorySerializer.get_configurations(instance, mandatory=True)
        )

        return serialized

    def deserialize(self, data, instance):
        instance.name = data.get('name', instance.name)
        instance.enabled = data.get('enabled', instance.enabled)

        instance.type = RepositoryType.query.filter_by(name=data.get('type')).one_or_none()

        configurations = data.get('configurations')

        if configurations:
            RepositoryConfiguration.query.filter(RepositoryConfiguration.repository == instance).delete()

            instance.configurations = [
                RepositoryConfiguration(
                    type_setting=RepositoryTypeSetting.query.join(RepositorySetting).filter(
                        RepositoryTypeSetting.type == instance.type,
                        RepositorySetting.name == name
                    ).one(),
                    value=value
                )
                for name, value in configurations.iteritems()
            ]

        return instance

    @staticmethod
    def get_configurations(instance, mandatory=False):
        return [
            type_setting.setting.name
            for type_setting in instance.type.type_settings
            if not mandatory or type_setting.mandatory
        ]
