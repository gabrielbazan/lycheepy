import os
from tempfile import mkdtemp
from werkzeug import secure_filename
from flask import request
from simplyrestful.serializers import Serializer
from simplyrestful.database import session
from simplyrestful.models import get_or_create
from simplyrestful.exceptions import Conflict, NotFound

from models import *
from validators import ProcessValidator
from gateways.processes import ProcessesGateway
from settings import *


class ProcessSerializer(Serializer):
    model = Process
    validators = [ProcessValidator]

    def create(self, data):
        self.save_file(data.get('identifier'))
        return super(ProcessSerializer, self).create(data)

    def update(self, identifier, data):
        self.save_file(data.get('identifier'), process_id=identifier)
        return super(ProcessSerializer, self).update(identifier, data)

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

    @staticmethod
    def _deserialize_parameter(model, process, parameter):
        format_name = parameter.get('format')
        data_type = parameter.get('dataType')
        return get_or_create(
            session,
            model,
            identifier=parameter.get('identifier'),
            title=parameter.get('title'),
            abstract=parameter.get('abstract'),
            process=process,
            format=Format.query.filter_by(name=format_name).one() if format_name else None,
            data_type=DataType.query.filter_by(name=data_type).one() if data_type else None
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
            ],
            metadata=[m.value for m in instance.meta_data]
        )

    def delete(self, identifier):
        try:
            instance = self.query.filter_by(id=identifier).one_or_none()

            if not instance:
                raise NotFound('The process does not exist')

            if instance.chains:
                raise Conflict('The process belongs to a chain, so it cannot be deleted')

            # Delete related objects
            session.query(ProcessMetadata).filter_by(process_id=identifier).delete()
            session.query(Output).filter_by(process_id=identifier).delete()
            session.query(Input).filter_by(process_id=identifier).delete()

            # Delete object
            session.delete(instance)

            # Delete process file
            ProcessSerializer.delete_file(instance.identifier)

            session.commit()
        except:
            session.rollback()
            raise

    def save_file(self, identifier, process_id=None):
        process_file = request.files.get(PROCESS_FILE_FIELD)

        if not process_id and not process_file:
            raise Conflict('The process file is required')

        if process_file:
            if not ProcessSerializer.is_valid_file(process_file.filename):
                raise Conflict('The process file extension is not accepted')

            if process_id:
                # Delete files for the previous identifier (in case it has been changed)
                process = self.query.filter_by(id=process_id).one()
                ProcessSerializer.delete_file(process.identifier)

            ProcessSerializer.create_file(identifier, process_file)

    @staticmethod
    def create_file(identifier, process_file):
        path = os.path.join(mkdtemp(), secure_filename(process_file.filename))
        process_file.save(path)
        ProcessSerializer.get_gateway().add(identifier, path)
        os.remove(path)

    @staticmethod
    def delete_file(identifier):
        return ProcessSerializer.get_gateway().remove(identifier)

    @staticmethod
    def is_valid_file(filename):
        return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_PROCESSES_EXTENSIONS

    @staticmethod
    def get_gateway():
        return ProcessesGateway(
            PROCESSES_GATEWAY_HOST,
            PROCESSES_GATEWAY_USER,
            PROCESSES_GATEWAY_PASS,
            PROCESSES_GATEWAY_TIMEOUT,
            PROCESSES_GATEWAY_DIRECTORY
        )
