from time import sleep
import re
from string import Template
from os.path import dirname, join
from xml.etree import ElementTree
import urlparse
from requests import post, get


class WpsGateway(object):

    def __init__(self, uri):
        self.uri = uri
        self.templates_directory = dirname(__file__)
        self.execute_template = 'wps_execute.xml'

    def execute(self, identifier, input_identifier, reference_uri):
        with open(join(self.templates_directory, self.execute_template), 'r') as template:
            get_records = template.read()

        response = post(
            self.uri,
            Template(get_records).safe_substitute(
                identifier=identifier, input=input_identifier, reference=reference_uri
            )
        )

        assert response.status_code == 200, 'WPS Execute operation did not respond with HTTP code 200'

        tree = ElementTree.ElementTree(ElementTree.fromstring(response.text)).getroot()
        status_location = tree.get('statusLocation')
        execution_id = re.search('(.*)/(.*).xml', status_location).group(2)

        seconds = .5
        finished = False
        timeout = 20
        time_counter = 0

        while not finished:

            assert time_counter < timeout, 'Asynchronous execution took more than {} seconds'.format(timeout)

            path = urlparse.urlparse(status_location).path

            status_response = get('{}/{}'.format(self.uri, path))

            assert status_response.status_code == 200, 'Failed to retrieve WPS execution Status Location'

            status = status_response.text
            status_tree = ElementTree.ElementTree(ElementTree.fromstring(status)).getroot()

            namespaces = dict(wps='http://www.opengis.net/wps/1.0.0')

            if status_tree.findall('wps:ProcessOutputs', namespaces):
                finished = True

            sleep(seconds)
            time_counter += seconds

        return execution_id
