import re
from xml.etree import ElementTree
import unittest
import json
from string import Template
from requests import post, get
from settings import *


class TestCosmoSkymed(unittest.TestCase):

    def setUp(self):
        self.create_processes()
        self.create_chain()

    def test_cosmo(self):
        execution_id = self.execute_chain()
        self.execution_is_published(execution_id)
        self.products_are_published(execution_id)

    def create_processes(self):
        for process in PROCESSES:
            if not self.process_exists(process.get('specification').get('identifier')):
                response = post(
                    PROCESSES_URL,
                    files=dict(
                        specification=(None, json.dumps(process.get('specification')), 'application/json'),
                        file=(process.get('file'), open(process.get('file'), 'rb'), 'application/octet-stream')
                    )
                )
                self.assertEqual(response.status_code, 201, 'Failed to create process {}'.format(process.get('identifier')))

    def create_chain(self):
        if not self.chain_exists(CHAIN.get('identifier')):
            response = post(CHAINS_URL, json=CHAIN)
            self.assertEqual(response.status_code, 201, 'Failed to create chain')

    def execute_chain(self):
        response = post(WPS_URL, CHAIN_EXECUTE)
        self.assertEqual(response.status_code, 200, 'Failed to execute chain')
        print response.text
        tree = ElementTree.ElementTree(ElementTree.fromstring(response.text)).getroot()
        status_location = tree.get('statusLocation')
        execution_id = re.search('(.*)/(.*).xml', status_location).group(2)
        return execution_id

    def execution_is_published(self, execution_id):
        response = get('{}?execution_id__eq={}'.format(EXECUTIONS_URL, execution_id))
        self.assertEqual(response.status_code, 200, 'Failed to query chain executions')
        results = response.json().get('results')
        self.assertTrue(bool(results), 'Chain execution is not published')
        self.assertTrue(results[0].get('status').get('name') == 'SUCCESS', 'Chain execution is published, but is not a success')

    def products_are_published(self, execution_id):
        response = post(CSW_URL, Template(CSW_GET_RECORDS).safe_substitute(execution_id=execution_id))
        self.assertEqual(response.status_code, 200, 'Failed to query execution products through CSW Get Records operation')
        tree = ElementTree.ElementTree(ElementTree.fromstring(response.text)).getroot()
        search_results = tree.find('csw:SearchResults', namespaces=dict(csw='http://www.opengis.net/cat/csw/2.0.2'))
        number_of_records = int(search_results.get('numberOfRecordsReturned'))
        self.assertEqual(
            number_of_records,
            5,
            'Failed to retrieve automatically published products. Obtained {} results'.format(number_of_records)
        )

    def process_exists(self, identifier):
        response = get('{}?identifier__eq={}'.format(PROCESSES_URL, identifier))
        self.assertEqual(response.status_code, 200, 'Failed to query process')
        return response.json().get('results')

    def chain_exists(self, identifier):
        response = get('{}?identifier__eq={}'.format(CHAINS_URL, identifier))
        self.assertEqual(response.status_code, 200, 'Failed to query chain')
        return response.json().get('results')


if __name__ == '__main__':
    unittest.main()
