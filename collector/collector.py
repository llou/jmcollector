
class Collector:
    """The root of the collection system, an object that represents the main 
    directory of the collection

    The collector object loads all collection definitions and verifies their
    state first if they are in the database or not, it can also verify the
    syncronization between tables and filesystems.

    So the state of the collection can be:
     * unloaded 
     * loaded
     * syncronized
     * not-syncronized
    """

    collections = []

    def __init__(self, path):
        self.path = path

    def iter_items(self):
        for collection in self.collections:
            for item in collection.iter_items(self):
                yield item

    def add_collection(self, collection):
        self.collections.append(collection)






