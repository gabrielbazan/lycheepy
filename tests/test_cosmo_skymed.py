from unittest import TestCase, main
from settings import CSW_URL, WPS_URL, PROCESSES_URL, CHAINS_URL, EXECUTIONS_URL, WCS_RASTER
from cosmo_settings import PROCESSES, CHAIN
from gateways import CswGateway, WpsGateway, ProcessesGateway, ChainsGateway, ExecutionsGateway


class TestCosmoSkymed(TestCase):

    def setUp(self):
        self.csw_gateway = CswGateway(CSW_URL)
        self.wps_gateway = WpsGateway(WPS_URL)
        self.processes_gateway = ProcessesGateway(PROCESSES_URL)
        self.chains_gateway = ChainsGateway(CHAINS_URL)
        self.executions_gateway = ExecutionsGateway(EXECUTIONS_URL)
        self.create_processes()
        self.create_chain()

    def test_cosmo(self):
        execution_id = self.execute_chain()
        self.execution_is_published(execution_id)
        self.products_are_published(execution_id)

    def create_processes(self):
        for process in PROCESSES:
            if not self.processes_gateway.exists(process['specification']['identifier']):
                response = self.processes_gateway.create(process.get('specification'), process.get('file'))
                self.assertEqual(
                    response.status_code, 201, 'Failed to create process {}'.format(process.get('identifier'))
                )

    def create_chain(self):
        if not self.chains_gateway.exists(CHAIN['identifier']):
            response = self.chains_gateway.create(CHAIN)
            self.assertEqual(response.status_code, 201, 'Failed to create chain')

    def execute_chain(self):
        return self.wps_gateway.execute(CHAIN['identifier'], 'crude', WCS_RASTER)

    def execution_is_published(self, execution_id):
        execution = self.executions_gateway.get(execution_id)
        self.assertEqual(
            execution['status']['name'], 'SUCCESS', 'Chain execution is published, but is not a success'
        )

    def products_are_published(self, execution_id):
        records_count = self.csw_gateway.get_records_count(execution_id)
        self.assertEqual(
            records_count,
            5,
            'Failed to retrieve automatically published products. Obtained {} results'.format(records_count)
        )


if __name__ == '__main__':
    unittest.main()
