

class Collection:
    """A logical abstraction of all the elements of the same collection.
    Now a directory in the Master directory, but can be in multiples locations
    in the future.

    It should include all the intrinsics of handling the collection, beeing the
    other classes auxiliaries of this one.
    """

    relative_path = None
    table_preffix= None
    item_class = Item
    file_class = File # You can personalize this object build_from_path to build
                      # sophiticated objects

    class Builder:
        def __init__(self):
            self.collector = None
            self.items = []

        def set_collector(self, collector):
            self.collector = collector

        def add_item(self, item):
            self.items.append(item)

        def build(self):
            return Collection(self.items, self.collector)


    def __init__(self, items, collector):
        self.items = items
        self.collector = collector
        self.path = Path(collector.path, self.relative_path)

    def add_item(self, item):
        self.items.append(item)
    
    def iter_items(self):
        for item in self.items:
            yield item

    def iter_files(self):
        for item in self.items:
            for file in item.iter_files():
                yield file
        
       def update_sha1(self):
        pass

    def validate_file(self, path):
        "Check if a file conforms the collection, in negative case it is ignored"
        return True

    def get_item_name_from_path(self, path):
        return path.name

    def get_item_metadata_from_path(self, path):
        return {}


class FileCollection(Collection):
    "A colection made of files"
    item_class = FileItem


class DirectoryCollection(Collection):
    "A colection made of directories"
    item_class = DirectoryItem


