import os
from urllib.parse import urlparse, unquote

# THis class name is bad, it's not really a slug
# The idea is clear to me, but the name isn't.
# I get an url, which might contain
# weird characters and structure and I want to
# save it on the file system, thus I need only legal
# characters, which this class is supposed to ensure

# Url --> FilePath
class Slug(object):
    '''A slug converts an url to a file path'''

    def __init__(self, url):
        self.url = url

    def _remove_invaild_characters(self, path):
        path = path.replace(',', '_')
        valid_characters = [c for c in path if not c in '<>:"|?*\':']
        return ''.join(valid_characters)

    def _domain_to_directory(self, url):
        url = url.replace('.', '-')
        return url

    def _path_to_directory(self, path):
        path = path.strip('/')
        path = path.replace('/', '-')
        path = path.replace(' ', '_')
        return path

    def _slug(self, url):
        url = unquote(url)
        fragments = urlparse(url)

        directory = self._domain_to_directory(fragments.netloc)

        path, file_fragment = os.path.split(fragments.path)
        path = self._path_to_directory(path)
        filename = file_fragment

        path = os.path.join(directory, path, filename)
        return self._remove_invaild_characters(path)

    def __str__(self):
        return self._slug(self.url)
