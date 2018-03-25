from repository import Repository
from geoserver.catalog import Catalog


class GeoServerRepository(Repository):

    def __init__(self, protocol, host, port, path='geoserver/rest', username='admin', password='geoserver', workspace='lycheepy'):
        self.url = '{}://{}:{}'.format(protocol, host, port)
        self.catalog = Catalog('{}/{}'.format(self.url, path), username=username, password=password)
        self.workspace = self._get_workspace(workspace)

    def _get_workspace(self, workspace_name):
        workspace = self.catalog.get_workspace(workspace_name)
        if not workspace:
            workspace = self.catalog.create_workspace(workspace_name, workspace_name)
        return workspace

    def publish(self, name, raster_file):
        self.catalog.create_coveragestore(name, raster_file, self.workspace, True)
        return '{}/geoserver/wcs?SERVICE=WCS&REQUEST=GetCoverage&VERSION=2.0.1&CoverageId={}'.format(
            self.url, name
        )
