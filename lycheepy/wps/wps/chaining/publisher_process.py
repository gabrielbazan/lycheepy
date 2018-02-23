from pywps import Process
from chaining.publication.repository import Repository


class PublisherProcess(Process):

    def __init__(self, *args, **kwargs):
        super(PublisherProcess, self).__init__(*args, **kwargs)

    def get_repository(self):
        return Repository()
