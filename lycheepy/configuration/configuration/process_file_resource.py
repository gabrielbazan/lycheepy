import os
from werkzeug import secure_filename
from flask import request
from simplyrestful.resources import Resource
from settings import ALLOWED_PROCESSES_EXTENSIONS, PROCESSES_TEMPORAL_DIRECTORY
from settings import PROCESSES_GATEWAY_HOST, PROCESSES_GATEWAY_USER, PROCESSES_GATEWAY_PASS
from settings import PROCESSES_GATEWAY_TIMEOUT, PROCESSES_GATEWAY_DIRECTORY
from processes_gateway import ProcessesGateway


class ProcessFileResource(Resource):

    gateway = ProcessesGateway(
        PROCESSES_GATEWAY_HOST,
        PROCESSES_GATEWAY_USER,
        PROCESSES_GATEWAY_PASS,
        PROCESSES_GATEWAY_TIMEOUT,
        PROCESSES_GATEWAY_DIRECTORY
    )

    def post(self):
        self.save()
        return 'Stored!', 201  # TODO

    def save(self):
        process_file = request.files.get('file')
        if process_file and self.is_valid_file(process_file.filename):
            self.gateway.add(self.save_locally(process_file))

    @staticmethod
    def is_valid_file(filename):
        return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_PROCESSES_EXTENSIONS

    @staticmethod
    def save_locally(process_file):
        path = os.path.join(PROCESSES_TEMPORAL_DIRECTORY, secure_filename(process_file.filename))
        process_file.save(path)
        return path
