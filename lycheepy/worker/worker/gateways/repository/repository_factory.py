from geo_server_repository import GeoServerRepository
from ftp_repository import FtpRepository


class Repositories(object):
    GEO_SERVER = 'GEO_SERVER'
    FTP = 'FTP'


class RepositoryFactory(object):
    map = {
        Repositories.GEO_SERVER: GeoServerRepository,
        Repositories.FTP: FtpRepository
    }

    @staticmethod
    def create(kind, configuration):
        print 'kind: ', kind
        print 'configuration: ', configuration
        if kind not in RepositoryFactory.map:
            raise NotImplementedError('Integration not implemented for "{}" repositories'.format(kind))
        return RepositoryFactory.map.get(kind)(**configuration)
