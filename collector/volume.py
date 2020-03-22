
class Volume:
    """Represents a group of items stored in the same removable media, normally
    a disk"""

    @classmethod
    def __init__(self, id, items):
        self.id = id
        self.items = items
