from sqlalchemy.sql import or_

from simplyrestful.database import session
from simplyrestful.models import get_or_create
from simplyrestful.serializers import Serializer

from lycheepy.models import *
from lycheepy.api.validators import *


class ProcessSerializer(Serializer):
    model = Process

    def deserialize(self, data, instance):
        instance.identifier = data.get('identifier', instance.identifier)
        instance.title = data.get('title', instance.title)
        instance.abstract = data.get('abstract', instance.abstract)
        instance.version = data.get('version', instance.version)

        inputs = data.get('inputs', [])
        outputs = data.get('outputs', [])
        metadata = data.get('metadata', [])

        instance.inputs = [self._deserialize_parameter(Input, instance, p) for p in inputs]
        instance.outputs = [self._deserialize_parameter(Output, instance, p) for p in outputs]
        instance.meta_data = [get_or_create(session, Metadata, value=m)[0] for m in metadata]

        return instance

    def _deserialize_parameter(self, model, process, parameter):
        return get_or_create(
            session,
            model,
            identifier=parameter.get('identifier'),
            title=parameter.get('title'),
            abstract=parameter.get('abstract'),
            process=process
        )[0]

    def serialize(self, instance):
        return dict(
            id=instance.id,
            identifier=instance.identifier,
            title=instance.title,
            abstract=instance.abstract,
            version=instance.version,
            inputs=[
                dict(
                    identifier=i.identifier,
                    title=i.title,
                    abstract=i.abstract
                )
                for i in instance.inputs
            ],
            outputs=[
                dict(
                    identifier=o.identifier,
                    title=o.title,
                    abstract=o.abstract
                )
                for o in instance.outputs
            ],
            metadata=[m.value for m in instance.meta_data]
        )


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

        instance.meta_data = [get_or_create(session, Metadata, value=m)[0] for m in metadata]

        instance.steps = self._deserialize_steps(instance, steps)

        return instance

    def _deserialize_steps(self, instance, steps):
        new_steps = [self._deserialize_step(s, instance) for s in steps]
        [session.delete(s) for s in instance.steps if s not in new_steps]
        return new_steps

    def _deserialize_step(self, s, chain):
        publish = s.get('publish', [])
        matches = s.get('match', [])
        before = Process.query.filter_by(identifier=s.get('before')).one()
        after = Process.query.filter_by(identifier=s.get('after')).one()

        step = get_or_create(session, Step, before=before, after=after, chain=chain)[0]

        step.publishables = [self._deserialize_step_output(o, before, after) for o in publish]
        step.matches = self._deserialize_step_matches(step, matches, before, after)

        return step

    def _deserialize_step_matches(self, step, matches, before, after):
        new_matches = [self._deserialize_step_match(m, before, after, step) for m in matches]
        [session.delete(m) for m in step.matches if m not in new_matches]
        return new_matches

    def _deserialize_step_output(self, output_identifier, before, after):
        return Output.query.filter(
            Output.identifier == output_identifier,
            or_(Output.process == before, Output.process == after)
        ).one()

    def _deserialize_step_match(self, m, before, after, step):
        output = Output.query.filter_by(process=before, identifier=m.get('output')).one()
        input = Input.query.filter_by(process=after, identifier=m.get('input')).one()
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
                    match=[
                        dict(
                            output=match.output.identifier,
                            input=match.input.identifier
                        )
                        for match in step.matches
                    ],
                    publish=[p.identifier for p in step.publishables]
                )
                for step in instance.steps
            ]
        )


class ExecutionSerializer(Serializer):
    model = Execution

    # TODO: Symplyrestful should format properties as camelcase automatically
    def serialize(self, instance):
        serialized = super(ExecutionSerializer, self).serialize(instance)
        serialized['chainIdentifier'] = serialized['chain_identifier']
        del serialized['chain_identifier']
        return serialized
