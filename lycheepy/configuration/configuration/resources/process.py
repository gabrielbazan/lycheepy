import json
from flask import request
from simplyrestful.resources import Resource
from serializers import ProcessSerializer


class ProcessResource(Resource):
    endpoint = 'processes'
    serializer = ProcessSerializer

    def post(self):
        return self._serializer.create(json.loads(request.form.get('data'))), 201

    def put(self, id):
        return self._serializer.update(id, json.loads(request.form.get('data')))
