from assistant.filesystem import *

DEFAULT_PATH = '.cached_files'


class Folder(object):
    '''Stores web responses such as PDFs on the file system'''
    def __init__(self, path=''):
        self._path = path or DEFAULT_PATH
        self._root = Directory(self._path)
        self._root.create()

    def store(self, path, content):
        file = (BinaryFile if path.endswith('pdf') else File)(path)
        # I don't know, but slashes look like the natural way
        # to combine paths...
        file = self._root / file
        file.directory.create()
        file.write(content)
        return file