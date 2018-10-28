from os.path import join, isfile

from flask import abort, send_from_directory
from flask_cors import CORS
from simplyrestful.app import app as application
from simplyrestful.settings import configure_from_module

configure_from_module('settings')

from pywps.configuration import get_config_value

from settings import CONFIGURATION_FILE, CONFIGURATION_URL
from service import ServiceBuilder
from executor import Executor


cross_origin = CORS(application, resources={r"*": {"origins": "*"}})


@application.route('/', methods=['GET', 'POST'])
def wps():
    return ServiceBuilder(
        Executor(),
        CONFIGURATION_FILE
    ).add_executables().build()


@application.route('/outputs/<path:filename>', methods=['GET'])
def output_file(filename):
    outputs_dir = get_config_value('server', 'outputpath')
    target_file = join(outputs_dir, filename)

    if isfile(target_file):
        return send_from_directory(outputs_dir, filename)
    else:
        abort(404)


if __name__ == '__main__':
    application.run(host='0.0.0.0', port=5001)
