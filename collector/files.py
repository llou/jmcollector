from pathlib import Path

class File:
    "Represents a file in the filesystem controlled by the collection"

    class Builder:
        def __init__(self):
            self.path = ""
            self.size = 0
            self.sha1 = ""

        def set_path(self, path):
            self.relative_path = Path(path)
            return self

        def set_size(self, value):
            self.size = value
            return self

        def set_sha1(self, sha1):
            self.sha1 = sha1
            return self

        def build(self):
            return File(self.path, self.size, sha1=self.sha1)

    def __init__(self, path, size, sha1=None):
        self.path = path
        self.size = size
        self.sha1 = sha1
        self.dirname = os.path.dirname(path)
        self.basename = os.path.basename(path)

    async def compute_hash(self, pool):
        self.sha1 = await pool.apply(get_sha1_file,[self.path])

    def __eq__(self, other):
        return repr(self) == repr(other)

    def __dict__(self):
        return {"path": str(self.path), "size": self.size, "sha1": self.sha1}

    def __repr__(self):
        if self.sha1 is None:
            return f"<File path:'{self.basename}'>"
        else:
            return f"<File path:'{self.basename}' sha1:'{self.sha1}'>"


class DirectoryItemFile(File):
    """Represents a File that it is inside a DirectoryItem.
    
    It is important to differenciate because the need to compute the hash of multiple
    files.
    """

    class Builder(File.Builder):
        def __init__(self):
            super().__init__()
            self.directory_item = None

        def set_directory_item(self, directory_item):
            self.directory_item = directory_item
            return self

        def build(self):
            return DirectoryItemFile(self.directory_item, self.relative_path, self.size, self.sha1)

    def __init__(self, directory_item, relative_path, size, sha1=None):
        self.directory_item = directory_item
        self.relative_path = relative_path
        self.relative_path_string = str(relative_path)
        super().__init__(Path(directory_item.relative_path, relative_path), size, sha1=sha1)

    def __str__(self):
        """Returns a representation of the file, its sha1 hash and separated one space the relative path
        within the directory, these are used latter to build the hash table of the
        DirectoryItem."""

        if self.sha1 is None:
            return str(self.relative_path)
        return f"{self.sha1} {self.relative_path}"

    def __lt__(self, other):
        return self.relative_path_string.__lt__(other.relative_path_string)

    def __le__(self, other):
        return self.relative_path_string.__le__(other.relative_path_string)

    def __ge__(self, other):
        return self.relative_path_string.__ge__(other.relative_path_string)

    def __gt__(self, other):
        return self.relative_path_string.__gt__(other.relative_path_string)

    def __dict__(self):
        return {"relative_path": str(self.relative_path), "size": self.size, 
                "sha1": self.sha1}

    def __repr__(self):
        if self.sha1 is None:
            return f"<DirectoryFile path:'{self.relative_path}'>"
        else:
            return f"<File path:'{self.relative_path}' sha1:'{self.sha1}'>"



