import os

from flask import Response, abort
from flask_cors import CORS
from simplyrestful.app import app
from simplyrestful.settings import configure_from_module

configure_from_module('settings')

from settings import HOST, PORT, DEBUG
from service import ServiceBuilder, ProcessesGateway, ChainsGateway

cross_origin = CORS(app, resources={r"*": {"origins": "*"}})

from pywps.configuration import get_config_value


@app.route('/wps', methods=['GET', 'POST'])
def wps():
    ChainsGateway._load_instances()  # TODO: Reload on chains CUD
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
