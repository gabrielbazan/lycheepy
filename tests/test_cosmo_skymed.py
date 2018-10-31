from unittest import TestCase, main
from settings import WPS_URL, PROCESSES_URL, CHAINS_URL, EXECUTIONS_URL, RASTER_DOWNLOAD_URL
from cosmo_settings import PROCESSES, CHAIN
from gateways import WpsGateway, ProcessesGateway, ChainsGateway, ExecutionsGateway


class TestCosmoSkymed(TestCase):

    def setUp(self):
        self.wps_gateway = WpsGateway(WPS_URL)
        self.processes_gateway = ProcessesGateway(PROCESSES_URL)
        self.chains_gateway = ChainsGateway(CHAINS_URL)
        self.executions_gateway = ExecutionsGateway(EXECUTIONS_URL)
        self.create_processes()
        self.create_chain()

    def test_cosmo(self):
        execution_id = self.execute_chain()
        self.execution_is_published(execution_id)

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
        return self.wps_gateway.execute(CHAIN['identifier'], 'crude', RASTER_DOWNLOAD_URL)

    def execution_is_published(self, execution_id):
        execution = self.executions_gateway.get(execution_id)
        self.assertEqual(
            execution['status']['name'], 'SUCCESS', 'Chain execution is published, but is not a success'
        )


if __name__ == '__main__':
    main()
