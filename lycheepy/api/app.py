import os

from flask import Response, send_from_directory, abort
from flask_cors import CORS
from simplyrestful.app import app, api
from simplyrestful.resources import add_resource
from simplyrestful.settings import configure_from_module

configure_from_module('lycheepy.settings')

from resources import *
from lycheepy.settings import HOST, PORT, DEBUG
from lycheepy.wps.service import ServiceBuilder, ProcessesFactory, ChainsFactory

cross_origin = CORS(app, resources={r"*": {"origins": "*"}})


add_resource(api, ProcessResource)
add_resource(api, ChainResource)
add_resource(api, ExecutionResource)


@app.route('/wps', methods=['GET', 'POST'])
def wps():
    return ServiceBuilder().extend(
        ProcessesFactory.create_all()
    ).extend(
        ChainsFactory.create_all()
    ).build()


@app.route('/outputs/' + '<filename>')
def output_file(filename):
    target_file = os.path.join('outputs', filename)
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

@app.route('/static/' + '<filename>')
def serve_static(filename):
    return send_from_directory(os.path.join('', 'static'), filename)


if __name__ == '__main__':
    app.run(host=HOST, port=PORT, debug=DEBUG, threaded=True)
