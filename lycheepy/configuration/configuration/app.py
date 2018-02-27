from flask_cors import CORS
from simplyrestful.app import app as application, api
from simplyrestful.resources import add_resource
from simplyrestful.settings import configure_from_module

configure_from_module('settings')

from resources import ProcessResource, ChainResource


cross_origin = CORS(application, resources={r"*": {"origins": "*"}})

add_resource(api, ProcessResource)
add_resource(api, ChainResource)
