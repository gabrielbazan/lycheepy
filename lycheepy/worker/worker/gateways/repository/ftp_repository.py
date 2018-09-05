from os.path import join, basename
from repository import Repository
from ftp import Ftp


class FtpRepository(Repository):

    def __init__(self, ip, username, password, timeout):
        self.connection = Ftp(ip, username, password, timeout)

    def publish(self, name, raster_file):
        with self.connection:
            self.connection.create_directory_if_not_exists(name)
            self.connection.upload_file(raster_file, join(name, basename(raster_file)))
