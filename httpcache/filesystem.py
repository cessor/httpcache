import os

PDF = '.pdf'


class NotADirectory(Exception):
    pass


class Directory(object):
    def __init__(self, path):
        self.path = path

    def _list_files(self):
        for file in os.listdir(self.path):
            path = os.path.join(self.path, file)
            yield File(path)

    def __iter__(self):
        return self._list_files().__iter__()

    def create(self):
        if not os.path.exists(self.path):
            os.makedirs(self.path)

    def __truediv__(self, other):
        # I don't know, but slashes look like the natural way
        # to combine paths...
        # __div__ just doesn't cut it... Thank you, isedev
        # http://stackoverflow.com/a/21859568/1203756
        if isinstance(other, Directory) or isinstance(other, File):
            ctor = type(other)
            # Creates Directory or File
            return ctor(os.path.join(self.path, other.path))

        raise NotADirectory()

    def __str__(self):
        return self.path


class Filename(object):
    def __init__(self, path):
        self.path = path

    def __str__(self):
        return os.path.split(self.path)[1]


class File(object):
    READ_FLAGS = 'r'
    WRITE_FLAGS = 'w'

    def __init__(self, path):
        self.path = path

    @property
    def directory(self):
        path = os.path.split(self.path)[0]
        return Directory(path)

    @property
    def name(self):
        return str(Filename(self.path))

    @property
    def content(self):
        with open(self.path, self.READ_FLAGS) as source:
            content = source.read()
        return content

    def write(self, content):
        with open(self.path, self.WRITE_FLAGS) as target:
            target.write(content)

    def __str__(self):
        return self.path


class BinaryFile(File):
    READ_FLAGS = 'rb'
    WRITE_FLAGS = 'wb'