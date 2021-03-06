from simplyrestful.database import session
from simplyrestful.models import get_or_create
from simplyrestful.serializers import Serializer
from models import *
from validators import ChainValidator


class ChainSerializer(Serializer):
    model = Chain
    validators = [ChainValidator]

    def deserialize(self, data, instance):
        instance.identifier = data.get('identifier', instance.identifier)
        instance.title = data.get('title', instance.title)
        instance.abstract = data.get('abstract', instance.abstract)
        instance.version = data.get('version', instance.version)

        steps = data.get('steps', [])
        metadata = data.get('metadata', [])
        publish = data.get('publish', [])

        instance.meta_data = [get_or_create(session, Metadata, value=m)[0] for m in metadata]

        instance.steps = self._deserialize_steps(instance, steps)

        instance.publishables = [
            self._deserialize_publishable(p, o) for p, outputs in publish.iteritems() for o in outputs
        ]

        return instance

    def _deserialize_publishable(self, process, output):
        return Output.query.filter(Output.identifier == output, Output.process.has(identifier=process)).one()

    def _deserialize_steps(self, instance, steps):
        new_steps = [self._deserialize_step(s, instance) for s in steps]
        [self._delete_step(s) for s in instance.steps if s not in new_steps]
        return new_steps

    def _delete_step(self, step):
        [session.delete(m) for m in step.matches]
        session.delete(step)

    def _deserialize_step(self, s, chain):
        matches = s.get('match', {})
        before = Process.query.filter_by(identifier=s.get('before')).one()
        after = Process.query.filter_by(identifier=s.get('after')).one()

        step = get_or_create(session, Step, before=before, after=after, chain=chain)[0]

        step.matches = self._deserialize_step_matches(step, matches, before, after)

        return step

    def _deserialize_step_matches(self, step, matches, before, after):
        new_matches = [self._deserialize_step_match(o, i, before, after, step) for o, i in matches.iteritems()]
        [session.delete(m) for m in step.matches if m not in new_matches]
        return new_matches

    def _deserialize_step_match(self, output, input, before, after, step):
        output = Output.query.filter_by(process=before, identifier=output).one()
        input = Input.query.filter_by(process=after, identifier=input).one()
        return get_or_create(session, StepMatch, input=input, output=output, step=step)[0]

    def serialize(self, instance):
        return dict(
            id=instance.id,
            identifier=instance.identifier,
            title=instance.title,
            abstract=instance.abstract,
            version=instance.version,
            metadata=[m.value for m in instance.meta_data],
            steps=[
                dict(
                    before=step.before.identifier,
                    after=step.after.identifier,
                    match={
                        match.output.identifier: match.input.identifier
                        for match in step.matches
                    }
                )
                for step in instance.steps
            ],
            publish=self._serialize_publish(instance),
            inputs=[
                dict(
                    identifier=i.identifier,
                    title=i.title,
                    abstract=i.abstract,
                    format=i.format.name if i.format else None,
                    dataType=i.data_type.name if i.data_type else None
                )
                for i in instance.inputs
            ],
            outputs=[
                dict(
                    identifier=o.identifier,
                    title=o.title,
                    abstract=o.abstract,
                    format=o.format.name if o.format else None,
                    dataType=o.data_type.name if o.data_type else None
                )
                for o in instance.outputs
            ]
        )

    def _serialize_publish(self, instance):
        publish = dict()
        for o in instance.publishables:
            p = o.process.identifier
            if p not in publish:
                publish[p] = []
            publish[p].append(o.identifier)
        return publish
