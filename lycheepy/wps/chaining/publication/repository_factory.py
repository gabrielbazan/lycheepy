from geo_server_repository import GeoServerRepository
from ftp_repository import FtpRepository


class RepositoryFactory(object):
    map = dict(
        GEO_SERVER=GeoServerRepository,
        FTP=FtpRepository
    )

    @staticmethod
    def create(kind, configuration):
        if kind not in RepositoryFactory.map:
            raise NotImplementedError('Integration not implemented for "{}" repositories'.format(kind))
        return RepositoryFactory.map.get(kind)(**configuration)
