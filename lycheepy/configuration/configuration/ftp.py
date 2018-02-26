import os
import ftplib


class Ftp(object):

    def __init__(self, ip, username, password, timeout):
        self._ftp = ftplib.FTP(ip, timeout=timeout)
        self._ftp.login(user=username, passwd=password)

    def __enter__(self):
        return self

    def __exit__(self, kind, value, tb):
        self.close()

    def close(self):
        self._ftp.quit()

    def upload_files(self, files, source, destination):
        for filename in files:
            self._ftp.storbinary(
                'STOR ' + os.path.join(destination, filename),
                open(os.path.join(source, filename), 'rb')
            )

    def download_file(self, remote_path, local_path):
        self._ftp.retrbinary('RETR ' + remote_path, open(local_path, 'wb').write)

    def upload_file(self, local_path, remote_path):
        self._ftp.storbinary('STOR ' + remote_path, open(local_path, 'rb'))

    def get_files_in_directory(self, directory):
        file_list = []
        for element in list(self._ftp.nlst(directory)):
            try:
                self._ftp.cwd(element)
            except ftplib.error_perm:
                file_list.append(os.path.basename(element))
        return file_list

    def directory_exist(self, path):
        current_path = self._ftp.pwd()
        exists = True
        try:
            self._ftp.cwd(path)
        except Exception:
            exists = False
        finally:
            self._ftp.cwd(current_path)
            return exists

    def create_directory(self, path):
        self._ftp.mkd(path)

    def delete_file(self, path):
        self._ftp.delete(path)

    def delete_directory(self, path):
        self._ftp.rmd(path)

    def is_up(self):
        try:
            self._ftp.retrlines('LIST')
        except Exception:
            return False
        return True
