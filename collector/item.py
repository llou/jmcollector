import hashlib
from pathlib import Path
from .file import File


class Item:
    "The basic element in all the collections"

    class Builder:
        def __init__(self):
            self.name = ""
            self.collection = None
            self.path = None
            self.relative_path = ""
            self.size = 0
            self.value = 5
            self.sha1 = ""
            self.volumes = []

        def set_name(self, name):
            self.name = name
            return self

        def set_collection(self, collection):
            self.collection = collection
            return self

        def set_path(self, path):
            self.path = path
            return self

        def set_relative_path(self, relative_path):
            self.relative_path = Path(relative_path)
            return self

        def set_size(self, size):
            self.size = size
            return self

        def set_value(self, value):
            self.value = value
            return self

        def set_sha1(self, sha1):
            self.sha1 = sha1
            return self

        def add_volume(self, volume):
            self.volumes.append(volume)
            return self

        def build(self):
            return Item(self.name,
                        self.collection,
                        self.path,
                        self.relative_path,
                        self.size,
                        value=self.value,
                        sha1=self.sha1,
                        volumes=self.volumes)


    def __init__(self, name, collection, path, relative_path, size, value=5, sha1="", 
                 volumes=[]):
        self.name = name
        self.path = path
        self.relative_path = relative_path
        self.size = size
        self.value = value
        self.volumes = volumes
        self.sha1 = sha1
        self.collection = None

    def set_collection(self, collection):
        self.collection = collection
        self.path = Path(collection.path, relative_path)

    @property
    def collector(self):
        return self.collection.collector

    def iter_files(self):
        raise NotImplemented

    @property
    def huge(self):
        return self.size > VOLUME_MAX_SIZE

    def get_alpha(self, total_volumes):
        return self.compute_alpha(self.value, len(self.volumes), total_volumes)

    def get_hash(self):
        "Returns an unique identifier of the item content"
        return self.sha1

    def __eq__(self, other):
        try:
            for attr in self.equality_attributes:
                if getattr(self, attr) != getattr(other, attr):
                    return False
            return True
        except AttributeError:
            return False

    def __repr__(self):
        return f"<Item:{self.__class__.__name__} '{self.path}'>"


class FileItem(Item):
    "An Item that consist of a singular file."

    @classmethod
    def is_directory(self):
        return False

    class Builder(Item.Builder):
        def __init__(self):
            self.file = None
            super().__init__()

        def set_file(self, file):
            self.file = file

        def build(self):
            return FileItem(self.file,
                            self.name,
                            self.collection,
                            self.relative_path,
                            self.size,
                            value=self.value,
                            sha1=self.sha1,
                            volumes=self.volumes)


    def __init__(self, file, name, collection, relative_path, size, value=5, 
                 sha1="", volumes=[]):
        self.file = file
        super().__init__(name, collection, relative_path, size, value=value, 
                         sha1=sha1, volumes=volumes)

    def iter_files(self):
        yield self.file

    def __eq__(self, other):
        try:
            return self.file == other.file
        except Exception:
            return False

    def __dict__(self, path):
        return self.file.__dict__()


class DirectoryItem(Item):
    "An item that consists of a directory that contains multiple files"

    @classmethod
    def is_directory(self):
        return True

    class Builder(Item.Builder):
        def __init__(self):
            self.files = []
            super().__init__()

        def add_file(self, file):
            self.files.append(file)

        def build(self):
            return DirectoryItem(self.files,
                                 self.name,
                                 self.collection,
                                 self.relative_path,
                                 self.size,
                                 value=self.value,
                                 sha1=self.sha1,
                                 volumes=self.volumes)

    def __init__(self, files, name, collection, relative_path, size, value=5, 
                 sha1="", volumes=[]):
        super().__init__(name, collection, relative_path, size, value=value, 
                         sha1=sha1, volumes=volumes)
        self.files = files
        self.files.sort()

    def compute_sha1(self):
        self.sha1_table = "\n".join([str(file) for file in self.files])
        self.sha1 = hashlib.sha1(self.sha1_table.encode("utf-8")).hexdigest()

    def __dict__(self, path):
        return {"name": self.name, "size": self.size,
                "files": [x.__dict__() for x in self.files]}


