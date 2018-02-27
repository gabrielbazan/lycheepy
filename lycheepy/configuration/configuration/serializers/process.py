import os
from werkzeug import secure_filename
from flask import request
from simplyrestful.serializers import Serializer
from simplyrestful.database import session
from simplyrestful.models import get_or_create

from models import *
from processes import ProcessesGateway
from index import IndexGateway
from settings import *


class ProcessSerializer(Serializer):
    model = Process

    processes = ProcessesGateway(
        PROCESSES_GATEWAY_HOST,
        PROCESSES_GATEWAY_USER,
        PROCESSES_GATEWAY_PASS,
        PROCESSES_GATEWAY_TIMEOUT,
        PROCESSES_GATEWAY_DIRECTORY
    )

    index = IndexGateway(
        INDEX_GATEWAY_HOST,
        INDEX_GATEWAY_PORT,
        INDEX_GATEWAY_DB
    )

    def create(self, data):
        self.save_file()
        serial = super(ProcessSerializer, self).create(data)
        self.index.publish(data.get('identifier'), serial)
        return serial

    def update(self, identifier, data):
        self.save_file()
        serial = super(ProcessSerializer, self).update(identifier, data)
        self.index.publish(identifier, serial)
        return serial

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

    def save_file(self):
        process_file = request.files.get('file')
        if process_file and self.is_valid_file(process_file.filename):
            self.processes.add(self.save_locally(process_file))

    @staticmethod
    def is_valid_file(filename):
        return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_PROCESSES_EXTENSIONS

    @staticmethod
    def save_locally(process_file):
        path = os.path.join(PROCESSES_TEMPORAL_DIRECTORY, secure_filename(process_file.filename))
        process_file.save(path)
        return path
