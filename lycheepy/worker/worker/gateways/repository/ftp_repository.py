from os.path import join, basename
from repository import Repository
from ftp import Ftp


class FtpRepository(Repository):

    def __init__(self, host, username, password, timeout, path=''):
        self.path = path
        self.connection = Ftp(host, username, password, timeout)

    def publish(self, name, raster_file):
        directory = join(self.path, name)

        with self.connection:
            self.connection.create_directory_if_not_exists(directory)
            self.connection.upload_file(raster_file, join(directory, basename(raster_file)))
