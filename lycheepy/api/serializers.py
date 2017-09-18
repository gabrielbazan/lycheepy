from simplyrestful.database import session
from simplyrestful.models import get_or_create
from simplyrestful.serializers import Serializer

from lycheepy.models import *


class ProcessSerializer(Serializer):
    model = Process

    def deserialize(self, data, instance):

        instance.identifier = data.get('identifier')
        instance.title = data.get('title')
        instance.abstract = data.get('abstract')
        instance.version = data.get('version')

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
        instance.identifier = data.get('identifier')
        instance.title = data.get('title')
        instance.abstract = data.get('abstract')
        instance.version = data.get('version')

        steps = data.get('steps', [])
        metadata = data.get('metadata', [])

        for m in metadata:
            instance.meta_data.append(
                get_or_create(session, Metadata, value=m)[0]
            )

        for s in steps:
            publish = s.get('publish', [])
            matches = s.get('match', [])
            before_id = Process.query.filter_by(identifier=s.get('before')).one().id
            after_id = Process.query.filter_by(identifier=s.get('after')).one().id
            step = Step(before_id=before_id, after_id=after_id)

            for output_identifier in publish:
                # TODO: Search for the output of the After process?
                output = Output.query.filter_by(process_id=before_id, identifier=output_identifier).one()
                step.publishables.append(output)

            for m in matches:
                output_id = Output.query.filter_by(process_id=before_id, identifier=m.get('output')).one().id
                input_id = Input.query.filter_by(process_id=after_id, identifier=m.get('input')).one().id
                step.matches.append(
                    StepMatch(input_id=input_id, output_id=output_id)
                )

            instance.steps.append(step)

        return instance

    def serialize(self, instance):
        return dict(
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
