from pathlib import Path
from multiprocessing import Pool, cpu_count 

DEFAULT_VALUE = 5

class CollectionConstructor:
    """An executive class that goes through the rough and wild data enviroments
    and manages to construct the system classes."""


    def __init__(self, collector, collection_class):
        self.collector = collector
        self.collection_class = collection_class
        self.relative_path = Path(self.collection_class.relative_path)
        self.path = Path(self.collector.path, self.relative_path)
        self.item_class = self.collection_class.item_class
        self.file_class = self.collection_class.file_class

    def prebuild_stuff(self, builder):
        "Here loads the items to the class"
        pass

    def postbuild_stuff(self, collection):
        "Here processes the items and integrates them into the collection" 
        pass

    def construct(self, relative_path):
        # Instantiates the Collection class builder
        builder = self.collection_class.Builder()
        # Sets the collector for the collection
        builder.set_collector(self.collector)
        # Invoques subclasses building stuff
        self.prebuild_stuff(builder)

        collection = builder.Build()
        # Let subclasses run some of their postbuild stuff
        self.postbuild_stuff(collection)

    def run_async_tasks(collection, pool):
        pass


class FileSystemCollectionInitializer(CollectionConstructor):

    def get_item_name_from_path(self, item_path):
        return self.collection_class.get_item_name_from_item_path(item_path)

    def collection_item_path_iterator(self, item_path):
        return self.collection_class.item_path_iterator(item_path

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
        # Iterates through all the items paths
        for item_abs_path in self.collection_item_path_iterator():
            # Creates a builder for each item path
            builder = self.item_class.Builder()
            # Sets the name
            builder.set_name(self.get_item_name_from_path(path))




    def postbuild_sturff(self, collection):
        # Iterates through the collection setting back references to upper
        # classes
        for item in collection.itet_items():
            item.set_collection(collection)
            for file in item.iter_files():
                file.set_item(item)
        collection_files = list(collection.iter_files())
        # Launch heavy computational stuff.
        pool = Pool(cpu_count())
        self.run_async_tasks(collection, pool)
        pool.join()

    async def postbuild_async_stuff(self, files, pool):
        for file in files:
            await file.awaitable_stuff(pool)


class JsonCollectionConstructor(Constructor):
    """An executive class that given a Json data file builds a complete structure
    of classes representing a collection"""
    pass

        
class DatabaseCollectionConstructor(Constructor):
    """An executive class that given a database content builds a complete structure
    of classes representing a collection"""
    pass

