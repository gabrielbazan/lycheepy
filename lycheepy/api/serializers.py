from simplyrestful.database import session
from simplyrestful.models import get_or_create
from simplyrestful.serializers import Serializer

from lycheepy.models import *


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

        for input in inputs:
            instance.inputs.append(
                Input(
                    identifier=input.get('identifier'),
                    title=input.get('title'),
                    abstract=input.get('abstract')
                )
            )

        for output in outputs:
            instance.outputs.append(
                Output(
                    identifier=output.get('identifier'),
                    title=output.get('title'),
                    abstract=output.get('abstract')
                )
            )

        for m in metadata:
            instance.meta_data.append(
                get_or_create(session, Metadata, value=m)[0]
            )

        return instance

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

    def deserialize(self, data, instance):
        instance.identifier = data.get('identifier', instance.identifier)
        instance.title = data.get('title', instance.title)
        instance.abstract = data.get('abstract', instance.abstract)
        instance.version = data.get('version', instance.version)

        steps = data.get('steps', [])
        metadata = data.get('metadata', [])

        instance.meta_data = [get_or_create(session, Metadata, value=m)[0] for m in metadata]

        instance.steps = [self._deserialize_step(s) for s in steps]

        return instance

    def _deserialize_step(self, s):
        publish = s.get('publish', [])
        matches = s.get('match', [])
        before = Process.query.filter_by(identifier=s.get('before')).one()
        after = Process.query.filter_by(identifier=s.get('after')).one()
        step = Step(before=before, after=after)

        for output_identifier in publish:
            # TODO: Search for the output of the After process?
            output = Output.query.filter_by(process=before, identifier=output_identifier).one_or_none()
            if not output:
                output = Output.query.filter_by(process=after, identifier=output_identifier).one_or_none()
            step.publishables.append(output)

        for m in matches:
            output = Output.query.filter_by(process=before, identifier=m.get('output')).one()
            input = Input.query.filter_by(process=after, identifier=m.get('input')).one()
            step.matches.append(
                StepMatch(input=input, output=output)
            )
        return step

    def serialize(self, instance):
        # TODO: Blows if an not-existent ID is requested
        # It should be solved by simplyrestful
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
