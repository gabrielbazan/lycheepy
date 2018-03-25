import json
from flask import request
from simplyrestful.resources import Resource
from simplyrestful.exceptions import Conflict
from serializers import ProcessSerializer
from settings import PROCESS_SPECIFICATION_FIELD


class ProcessResource(Resource):
    endpoint = 'processes'
    serializer = ProcessSerializer

    def post(self):
        self._validate_multipart()
        return self._serializer.create(json.loads(request.form.get(PROCESS_SPECIFICATION_FIELD))), 201

    def put(self, id):
        self._validate_multipart()
        return self._serializer.update(id, json.loads(request.form.get(PROCESS_SPECIFICATION_FIELD)))

    @staticmethod
    def _validate_multipart():
        if not request.form:
            raise Conflict('This endpoint only accepts multipart/form-data')
