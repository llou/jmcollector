from pathlib import Path
import asyncio
from multiprocessing import Pool, cpu_count 

DEFAULT_VALUE = 5

class CollectionConstructor:
    """An executive class that goes through the rough and wild data enviroments
    and manages to construct the system classes."""

    def __init__(self, collector, collection_class):
        self.collector = collector
        self.collection_class = collection_class
        self.relative_path = Path(self.collection_class.relative_path)
        self.collection_path = Path(self.collector.path, self.relative_path)
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


class FileSystemCollectionConstructor(CollectionConstructor):

    def get_item_name_from_path(self, item_path):
        return self.collection_class.get_item_name_from_item_path(item_path)

    def collection_item_path_iterator(self, collection_path):
        return self.collection_class.collections_item_path_iterator(collection_path)

    def collection_file_path_iterator(self, item_path):
        return self.collection_class.items_file_path_iterator(item_path)

    def get_file_builder_from_relative_path(self, file_relative_path):
        return self.collection_class.get_file_builder_from_relative_path(file_relative_path)

    def prebuild_stuff(self, collection_builder):
        # Iterates through all the items paths
        for item_path in self.collection_item_path_iterator(self.collection_path):
            # Creates a builder for each item path
            ibuilder = self.item_class.Builder()
            # Sets the name
            ibuilder.set_name(self.get_item_name_from_path(item_path))
            # Sets the path
            ibuilder.set_path(item_path)
            # Sets the relative path
            ibuilder.set_relative_path(item_path.relative_to(self.collection_path))
            # Checks for one of the two kinds of dirs
            if self.item_class.is_directory():
                # Request collection for an iterator of files
                for file_path in self.collection_file_path_iterator(item_path):
                    file_relative_path = file_path.relative_to(item_path)
                    # Request collection for a builder class given rel path
                    fbuilder = self.get_file_builder_from_relative_path(file_relative_path)
                    # Set minimum parapeters for file before building
                    fbuilder.set_path(file_path)
                    fbuilder.set_relative_path(file_relative_path)
                    # Builds the file
                    f = fbuilder.build()
                    # Adds the file to the item bulder
                    ibuilder.add_file(f)
            else:
                # In case thats is a single file collection
                fbuilder = self.collection_class.file_class.Build()
                fbuilder.set_path(file_path)
                # Buildes the file
                f = fbuilder.build()
                ibuilder.set_file(f)
            # Builds item
            item = ibuilder.build()
            collection_builder.add_item(item)

    def postbuild_stuff(self, collection):
        # Iterates through the collection setting back references to upper
        # classes
        for item in collection.iter_items():
            item.set_collection(collection)
            for file in item.iter_files():
                file.set_item(item)
        # Launch heavy computational stuff.
        pool = Pool(cpu_count())
        asyncio.run(self.postbuild_async_stuff(collection, pool))
        pool.join()

    async def postbuild_async_stuff(self, collection, pool):
        for file in collection.iter_files():
            await file.awaitable_stuff(pool)
        for item in collection.iter_items():
            await item.awaitable_stuff(pool)


class JsonCollectionConstructor(Constructor):
    """An executive class that given a Json data file builds a complete structure
    of classes representing a collection"""
    pass

        
class DatabaseCollectionConstructor(Constructor):
    """An executive class that given a database content builds a complete structure
    of classes representing a collection"""
    pass

