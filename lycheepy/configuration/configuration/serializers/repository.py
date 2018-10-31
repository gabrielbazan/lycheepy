from simplyrestful.database import session
from simplyrestful.serializers import Serializer
from models import Repository, RepositoryType, RepositoryConfiguration, RepositoryTypeSetting, RepositorySetting
from validators import RepositoryValidator


class RepositorySerializer(Serializer):
    model = Repository
    validators = [RepositoryValidator]

    def serialize(self, instance):
        serialized = super(RepositorySerializer, self).serialize(instance)

        del serialized['type_id']
        del serialized['deleted']

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

        if not instance.type:
            instance.type = RepositoryType.query.filter_by(name=data.get('type')).one()

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

    def _delete(self, identifier):
        instance = self._get_instance(identifier)
        instance.name = None  # Not longer taken into account for name uniqueness
        instance.enabled = False
        instance.deleted = True
        session.add(instance)

    def _list_filters(self):
        return self.model.deleted == False,

    def list(self, filtering):
        from simplyrestful.filtering import Filter
        try:
            filters = Filter(self.model, filtering)

            query = self.query.join(
                * filters.joins
            ).filter(
                * self._list_filters()
            ).filter(
                filters.orm_filters
            ).order_by(
                * filters.order_by
            )

            return dict(
                results=[
                    self.serialize(m)
                    for m in query.limit(filters.limit).offset(filters.offset).all()
                ],
                count=query.count()
            )
        except:
            session.rollback()
            raise
