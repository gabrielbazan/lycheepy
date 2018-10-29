from simplyrestful.resources import Resource
from serializers import RepositorySerializer


class RepositoryResource(Resource):
    endpoint = 'repositories'
    serializer = RepositorySerializer
