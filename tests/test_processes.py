from json import loads
from uuid import uuid4
from unittest import TestCase
from settings import PROCESSES_URL, PROCESS_SPECIFICATION, PROCESS_FILE
from gateways.processes import ProcessesGateway


class TestProcesses(TestCase):

    def setUp(self):
        self.gateway = ProcessesGateway(PROCESSES_URL)

    def test_list(self):
        response = self.gateway.list()
        self.assertEqual(response.status_code, 200)
        TestProcesses.assert_json(response.text)

    def test_create(self):
        identifier, response = self.create_process()
        self.assertEqual(response.status_code, 201, 'The process creation request did not respond with HTTP code 201')
        TestProcesses.assert_json(response.text)
        self.assertEqual(response.json()['identifier'], identifier)

    def test_update(self):
        identifier, response = self.create_process()

    def test_delete(self):
        identifier, response = self.create_process()
        response = self.gateway.delete(response.json()['id'])
        self.assertEqual(response.status_code, 204)
        self.assertEqual(response.text, '')

    def test_delete_and_create_again(self):
        identifier, response = self.create_process()

        self.gateway.delete(response.json()['id'])

        identifier, response = self.create_process(identifier)

        self.assertEqual(response.status_code, 201, 'The process creation request did not respond with HTTP code 201')
        TestProcesses.assert_json(response.text)
        self.assertEqual(response.json()['identifier'], identifier)

    def create_process(self, identifier=None):
        identifier = identifier if identifier else str(uuid4())
        specification = PROCESS_SPECIFICATION.copy()
        specification['identifier'] = identifier
        return identifier, self.gateway.create(specification, PROCESS_FILE)

    @staticmethod
    def assert_json(text):
        try:
            loads(text)
        except:
            raise AssertionError('Not a JSON: "{}"'.format(text))
