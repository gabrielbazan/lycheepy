from simplyrestful.app import app, api
from simplyrestful.resources import add_resource
from simplyrestful.settings import configure_from_module

configure_from_module('settings')

from resources import *
from settings import HOST, PORT, DEBUG


add_resource(api, ProcessResource)
add_resource(api, ChainResource)


if __name__ == '__main__':
    app.run(host=HOST, port=PORT, debug=DEBUG)
