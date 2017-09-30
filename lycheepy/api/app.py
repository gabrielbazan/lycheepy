import os

from flask import Response, abort
from flask_cors import CORS
from simplyrestful.app import app, api
from simplyrestful.resources import add_resource
from simplyrestful.settings import configure_from_module

configure_from_module('lycheepy.settings')

from lycheepy.api.resources import *
from lycheepy.settings import HOST, PORT, DEBUG
from lycheepy.wps.service import ServiceBuilder, ProcessesGateway, ChainsGateway

cross_origin = CORS(app, resources={r"*": {"origins": "*"}})

from pywps.configuration import get_config_value


add_resource(api, ProcessResource)
add_resource(api, ChainResource)
add_resource(api, ExecutionResource)


@app.route('/wps', methods=['GET', 'POST'])
def wps():
    return ServiceBuilder().extend(
        ProcessesGateway.all()
    ).extend(
        ChainsGateway.all()
    ).build()


@app.route('/wps/outputs/<execution_id>/<filename>')
def output_file(execution_id, filename):
    ServiceBuilder().build()
    outputs_dir = get_config_value('server', 'outputpath')
    target_file = os.path.join(outputs_dir, execution_id, filename)
    if os.path.isfile(target_file):
        file_ext = os.path.splitext(target_file)[1]
        with open(target_file, mode='rb') as f:
            file_bytes = f.read()
        mime_type = None
        if 'xml' in file_ext:
            mime_type = 'text/xml'
        return Response(file_bytes, content_type=mime_type)
    else:
        abort(404)


if __name__ == '__main__':
    app.run(host=HOST, port=PORT, debug=DEBUG, threaded=True)
