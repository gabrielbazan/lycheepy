from abc import ABCMeta, abstractmethod


class Repository(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def publish_raster(self, process, name, raster_file): raise NotImplementedError

    @abstractmethod
    def publish_features(self, process, name, features_file): raise NotImplementedError
