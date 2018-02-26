from flask_cors import CORS
from simplyrestful.app import app as application, api
from simplyrestful.resources import add_resource
from simplyrestful.settings import configure_from_module

configure_from_module('settings')

from resources import *
from process_file_resource import ProcessFileResource


cross_origin = CORS(application, resources={r"*": {"origins": "*"}})

add_resource(api, ProcessResource)
add_resource(api, ChainResource)
add_resource(api, ExecutionResource)
add_resource(api, ProcessFileResource)
