from repository import Repository


class FtpRepository(Repository):
    def publish_raster(self, name, raster_file): pass

    def publish_features(self, name, features_file): raise NotImplementedError
