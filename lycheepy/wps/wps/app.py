from os.path import join, isfile

from flask import abort, send_from_directory
from flask_cors import CORS
from simplyrestful.app import app as application
from simplyrestful.settings import configure_from_module

configure_from_module('settings')

from pywps.configuration import get_config_value

from settings import *
from service import ServiceBuilder

cross_origin = CORS(application, resources={r"*": {"origins": "*"}})


@application.route('/', methods=['GET', 'POST'])
def wps():
    return ServiceBuilder(
        CONFIGURATION_FILE,
        CONFIGURATION_URL
    ).add_executables().build()


@application.route('/outputs/<execution_id>/<filename>', methods=['GET'])
def output_file(execution_id, filename):
    outputs_dir = get_config_value('server', 'outputpath')
    execution_dir = join(outputs_dir, execution_id)
    target_file = join(execution_dir, filename)

    if isfile(target_file):
        return send_from_directory(execution_dir, filename)
    else:
        abort(404)


if __name__ == '__main__':
    application.run(host='0.0.0.0', port=5001)
