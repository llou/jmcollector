from pathlib import Path
from multiprocessing import Pool, procount

DEFAULT_VALUE = 5

class CollectionConstructor:
    """An executive class that goes through the rough and wild data enviroments
    and manages to construct the system classes."""

    collection_class = Collection

    def __init__(self, collector):
        self.collector = collector
        self.relative_path = Path(self.collection_class.relative_path)
        self.item_class = Path(self.collection_class.relative_path)
        self.file_class = Path(self.collection_class.file_class)
        self.path = Path(self.collector.path, relative_path)

    def prebuild_stuff(self, builder):
        "Here loads the items to the class"
        pass

    def postbuild_stuff(self, collection):
        "Here processes the items and integrates them into the collection" 
        pass

    def construct(self, relative_path):
        builder = self.collection_class.Builder()
        builder.set_collector(self.collector)
        self.prebuild_stuff(builder)
        collection = builder.Build()
        self.postbuild_stuff(collection)
        pool = Pool(proccount())
        asyncio.run(self.run_async_tasks(collection.iter_files, pool))
        pool.join()

    async def run_async_tasks(col


class FileSystemInitializer(Constructor):
    "An object that grabs data from the file system and builds a collection"
    "into the database"

    collection_class = Collection

    def __init__(self, collector):
        super().__init__(collector)

    def get_item_name_from_path(self, path):
        return path.name

    def item_path_iterator(self):
        "Iter the main directory of the collection for items"
        for item_path in self.path.iterdir():
            yield item_path

    def file_path_iterator(self, item_path):
        "Iter the contents of a DirectoryItem"
        for dirname, subdirs, files in os.walk(item_path):
            for f in files:
                yield f

    def item_get_path_files(self, item_path):
        if path.isfile():
            return [self.build_file(path)]
        if path.isdir():
            result = []
            for file_path in self.file_path_iterator(path):
                result.append(self.build_file(file_path))
            return result

    def build_file(file_path):
        builder = self.file_class.Builder()
        builder.set_path(file_path)
        return builder.build()

    def prebuild_stuff(self, collection_builder):
        for item_abs_path in self.item_path_iterator():
            item_builder = self.item_class.Builder()
            item_builder.set_name(self.get_item_name_from_path())
            item_builder.set_relative_path(item_abs_path.relative_to(self.path))
            item_files = self.iitem_get_path_files(item_abs_path)
            if isinstance(self.item_class, FileItem):
                item_builder.set_file(item_files[0])
            elif isinstance(self.item_class, DirectoryItem):
                for file in self.item_files:
                    item_builder.add_file(file)
            item = item_builder.build()
            collection_builder.add(item)

    def postbuild_sturff(self, collection):
        for item in collection.items:
            item.set_collection(collection) 
        collection_files = list(collection.iter_files())
        pool = multiprocessing.Pool(8)
        asyncio.run(self.postbuild_async_stuff(files, poool))
        pool.join()

    async def postbuild_async_stuff(self, files, pool):
        for file in files:
            await file.awaitable_stuff(pool)


class JsonDumpConstructor(Constructor):
    """An executive class that given a Json data file builds a complete structure
    of classes representing a collection"""
    pass

        
class DatabaseConstructor(Constructor):
    """An executive class that given a database content builds a complete structure
    of classes representing a collection"""
    pass

