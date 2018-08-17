from string import Template
from os.path import dirname, join
from xml.etree import ElementTree
from requests import post


class CswGateway(object):

    def __init__(self, uri):
        self.uri = uri
        self.templates_directory = dirname(__file__)
        self.get_records_template = 'csw_get_records.xml'

    def get_records_count(self, search_text):
        with open(join(self.templates_directory, self.get_records_template), 'r') as template:
            get_records = template.read()

        response = post(self.uri, Template(get_records).safe_substitute(search_text=search_text))

        assert response.status_code == 200, 'CSW Get Records operation did not respond with HTTP code 200'

        tree = ElementTree.ElementTree(ElementTree.fromstring(response.text)).getroot()
        search_results = tree.find('csw:SearchResults', namespaces=dict(csw='http://www.opengis.net/cat/csw/2.0.2'))

        return int(search_results.get('numberOfRecordsReturned'))
