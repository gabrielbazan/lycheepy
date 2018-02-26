from ftp import Ftp


class ProcessesGateway(object):

    def __init__(self, host, user, password, timeout, directory):
        self.connection = Ftp(host, user, password, timeout)
        self.directory = directory

    def add(self, process_file_path):
        with self.connection:
            self.connection.upload_file(process_file_path, self.directory)

    def get(self, remote_file_path, local_destination_path):
        with self.connection:
            self.connection.download_file(remote_file_path, local_destination_path)

    def remove(self, remote_file_path):
        with self.connection:
            self.connection.delete_file(remote_file_path)
