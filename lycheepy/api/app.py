from flask_cors import CORS
from simplyrestful.app import app, api
from simplyrestful.resources import add_resource
from simplyrestful.settings import configure_from_module

configure_from_module('lycheepy.settings')

from lycheepy.api.resources import *
from lycheepy.settings import HOST, PORT, DEBUG
from lycheepy.wps.service import ServiceBuilder, ProcessesGateway, ChainsGateway

cross_origin = CORS(app, resources={r"*": {"origins": "*"}})


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


if __name__ == '__main__':
    app.run(host=HOST, port=PORT, debug=DEBUG, threaded=True)
