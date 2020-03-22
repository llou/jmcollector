from pathlib import Path
from crypto import get_sha1_file

class File:
    "Represents a file in the filesystem controlled by the collection"

    class Builder:
        def __init__(self):
            self.path = ""
            self.size = 0
            self.sha1 = ""
            self.item = None

        def set_path(self, path):
            self.relative_path = Path(path)
            return self

        def set_size(self, value):
            self.size = value
            return self

        def set_sha1(self, sha1):
            self.sha1 = sha1
            return self

        def set_item(self, item):
            self.item = item
            return self

        def build(self):
            return File(self.path, self.size, sha1=self.sha1, item=None)

    def __init__(self, path, size, sha1=None, item=None):
        self.path = path
        self.size = size
        self.sha1 = sha1
        if item is not None:
            self.set_item(item)
        else:
            self.relative_path = None

    def set_item(self, item):
        self.item = item
        self.relative_path = self.path.relative_to(item.path)
        self.relative_path_string = str(self.relative_path)

    def set_sha1(self, sha1):
        self.sha1 = sha1

    def compute_hash(self, pool):
          pool.apply_async(get_sha1_file,[self.path], 
                           self.set_sha1)

    def __eq__(self, other):
        return repr(self) == repr(other)


    def __dict__(self):
        return {"path": str(self.path), "size": self.size, "sha1": self.sha1}

    def __repr__(self):
        if self.sha1 is None:
            return f"<File path:'{self.path.name}'>"
        else:
            return f"<File path:'{self.path.name}' sha1:'{self.sha1}'>"


class FileItemFile(File):
    def __repr__(self):
        if self.sha1 is None:
            return f"<FileItemFile (path:'{self.path.name}')>"
        else:
            return f"<FileItemFile (path:'{self.path.name}', sha1:'{self.sha1}')>"


class DirectoryItemFile(File):
    
    def __init__(self, path, size, sha1=None, item=None):
        self.relative_path = ""
        self.relative_path_string = ""
        super().__init__(pat, size, sha1=sha1, item=item)
    
    def set_item(self, item):
        self.item = item
        self.relative_path = self.path.relative_to(item.path)
        self.relative_path_string = str(self.relative_path)

    def __lt__(self, other):
        return self.relative_path_string.__lt__(other.relative_path_string)

    def __le__(self, other):
        return self.relative_path_string.__le__(other.relative_path_string)

    def __ge__(self, other):
        return self.relative_path_string.__ge__(other.relative_path_string)

    def __gt__(self, other):
        return self.relative_path_string.__gt__(other.relative_path_string)

    def __repr__(self):
        if self.sha1 is None:
            return f"<DirectoryItemFile (path:'{self.path.name}')>"
        else:
            return f"<DirectoryItemFile (path:'{self.path.name}', sha1:'{self.sha1}')>"
