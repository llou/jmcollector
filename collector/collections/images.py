from ..jmcollector import *
class ImageFile(File):
    async def awaitable_stuff(self, pool):
        await super().awaitable_stuff(pool)
        await self.compute_thumnail(pool)

    async def compute_thumbnail(self, pool):
        await pool.apply(compute_thumnail, [self.relative_path, self.thumbnail_path, 

class ImageItem(FileItem):
    """Image item consists of two files the main image file and the thumbnail
    one, the managemenent is simplified as both share the same relative_path
    """

    class Builder(Item.Builder):
        def __init__(self):
            super().__init__()
            self.thumbnail_sha1=""

        def set_thumbnail_sha1(self, sha1):
            self.thumbnail_sha1=sha1

        def build(self):
            return ImageItem(self.name,
                        self.collection,
                        self.relative_path,
                        self.size,
                        value=self.value,
                        sha1=self.sha1,
                        thumbnail_sha1=self.thumbnail_sha1,
                        volumes=self.volumes)
    
    def __init__(self, name, collection, relative_path, size, value=5, 
                 sha1="", thumbnail_sha1="", volumes=[]):
        super().__init__(name, collection, relative_path, size, value=value, 
                         sha1=sha1, volumes=volumes)
        self.thumbnail_sha1=thumbnail_sha1()


class ImageCollection(FileCollection):
    file_class = "ImageFile"
    thumbnail_path = ".thumbnails"


class ImageCollectionFileSystemInitializer(FileSystemInitializer):
    collection_class = ImageCollection

    def prebuild_stuff(self, collection_builder):
        item_class = self.collection_class.item_class
        for path in self.path.iterdir():
            item_builder = item_class.Builder()
            item_builder.set_name(path.name())
            item_builder.set_pat(path)
            item_builder.set_size(path.stat().size)
            item = item_builder.build()
            collection_builder.add_item(item)

    def postbuild_sturff(self, collection):
        for item in collection.items:
            item.set_collection(collection)



class ImageCollectionDatabaseConstructor(DatabaseConstructor):
    collection_class = ImageCollection
    items_table = None

    def prebuild_stuff(self, builder):
        pass

    def postbuild_sturff(self, collection):
        pass

        
class ImageCollectionJsonDump(DatabaseConstructor):
    collection_class = ImageCollection
    items_table = None

    def prebuild_stuff(self, builder):
        pass

    def postbuild_sturff(self, collection):
        pass
 
