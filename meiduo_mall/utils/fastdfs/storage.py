import os

from django.core.files.storage import Storage
from django.conf import settings


def get_file_ext_name(filename):
    return os.path.splitext(filename)[1].lstrip('.')

class MyStorage(Storage):
    def _open(self, name, mode='rb'):
        raise NotImplementedError('FastDFS storage does not support opening files.')

    def _save(self, name, content, max_length=None):
        from fdfs_client.client import Fdfs_client

        client = Fdfs_client(settings.FDFS_CLIENT_CONF)
        file_ext_name = get_file_ext_name(name)
        result = client.upload_by_buffer(content.read(), file_ext_name)

        if result.get('Status') != 'Upload successed.':
            raise Exception('Upload file to FastDFS failed.')

        return result.get('Remote file_id')

    def exists(self, name):
        return False

    def url(self, name):
        if name.startswith(('http://', 'https://')):
            return name

        return settings.FDFS_BASE_URL.rstrip('/') + '/' + name.lstrip('/')
