from ftplib import FTP


class Ftp(object):

    def __init__(self, ip, username, password, timeout):
        self.connection = FTP(ip, timeout=timeout)
        self.connection.login(user=username, passwd=password)

    def __enter__(self):
        return self

    def __exit__(self, kind, value, tb):
        self.close()

    def close(self):
        self.connection.quit()

    def upload_file(self, local_path, remote_path):
        self.connection.storbinary('STOR ' + remote_path, open(local_path, 'rb'))

    def create_directory_if_not_exists(self, path):
        if not self.directory_exists(path):
            self.create_directory(path)

    def directory_exists(self, path):
        current_path = self.connection.pwd()
        exists = True
        try:
            self.connection.cwd(path)
        except Exception:
            exists = False
        finally:
            self.connection.cwd(current_path)
            return exists

    def create_directory(self, path):
        self.connection.mkd(path)
