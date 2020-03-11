#! /usr/bin/env python
"""
jmcolector
=========

Manages your collection of data.
"""

import sys
import os
import hashlib
from subprocess import run, PIPE
from multiprocessing import Pool, cpu_count
from pathlib import Path
import logging
import argparse
import platform
import json
import psycopg2
from yaml import load, dump
try:
    from yaml import CLoader as YLoader, CDumper as YDumper
except ImportError:
    from yaml import Loader as YLoader, Dumper as YDumper

# Logging stuff

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(levelname)s - %(message)s")
ch.setFormatter(formatter)
logger.addHandler(ch)

# Platform stuff

platform = platform.platform()
if platform[0:5] == "macOS":
    platform = "MACOS"
elif platform[0:5] == "Linux":
    platform = "LINUX"
elif platform[0:7] == "WINDOWS":
    platform = "WINDOWS"
else:
    print("System Unknown")
    sys.exit(1)

# Constants

DIRECTORY_STRUCTURE = {}
VOLUME_MAX_SIZE = 4300 * 1024 * 1024
TAG = ".jmtag"
INFO_PATH = ".jminfo/data.yml"
EXCLUDED_FILES = [TAG]
MASTER_PATH="~/Dropbox"
COLLECTION_SETTINGS="jmcollector.yml"

# Criptographic stuff


def get_sha1_file(path):
    if platform in ["LINUX","MACOS"]:
        if platform == "LINUX":
            p = run(["/usr/bin/shasum", path], stdout=PIPE, stderr=PIPE)
        elif platform == "MACOS":
            p = run(["/usr/bin/shasum", "-a", "1", path], stdout=PIPE, stderr=PIPE)
        if p.returncode:
            print("Error processing file %s." % path)
            sys.exit(1)
        return p.stdout.decode("utf-8").split(" ")[0]
    else:
        BUF_SIZE = 65536  # lets read stuff in 64kb chunks!
        sha1 = hashlib.sha1()
        with open(sys.argv[1], 'rb') as f:
            while True:
                data = f.read(BUF_SIZE)
                if not data:
                    break
                sha1.update(data)
        return sha1.hexdigest()

def get_sha1_var(data):
    sha1 = hashlib.sha1()
    sha1.update(data)
    return sha1.hexdigest()

def compute_hashes(paths):
    with Pool(cpu_count()) as pool:
        return pool.map(get_sha1_file, paths)

# Class definitions

class File:
    "Represents a file in the filesystem controlled by the collection"

    @classmethod
    def build_from_path(cls, path, compute_hash=False):
        path = Path(path)
        stat = path.stat()
        size = stat.st_size
        sha1 = get_sha1_file(path) if compute_hash else None
        return cls(path, size, sha1=sha1)

    @classmethod
    def validate(cls, path):
        return True

    def __init__(self, path, size, sha1=None):
        self.path = Path(path)
        self.size = size
        self.sha1 = sha1
        self.dirname = os.path.dirname(path)
        self.basename = os.path.basename(path)

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

    @classmethod
    def build_from_file(cls, directory_item, file):
        relative_path = file.path.relative_to(directory_item.relative_path)
        return cls(directory_item, relative_path, file.size, sha1=file.sha1)

    def __init__(self, directory_item, relative_path, size, sha1=None):
        self.directory_item = directory_item
        self.relative_path = relative_path
        self.relative_path_string = str(relative_path)
        super().__init__(Path(directory_item.relative_path, relative_path), size, sha1=sha1)

    def __str__(self):
        """Returns a representation of the file, its sha1 hash and separated one space the relative        path within the directory, these are used latter to build the hash
        table of the DirectoryItem."""

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


class Item:
    "The basic element in all the collections"
    equality_attributes = ["name", "collection", "relative_path"]
    is_dir = None


    def __init__(self, name, collection, relative_path, size, value=5, sha1=""):
        self.name = name
        self.collection = collection
        self.relative_path = Path(relative_path)
        self.path = Path(collection.path, relative_path)
        self.size = size
        self.value = value
        self.sha1 = sha1

    @property
    def collector(self):
        return self.collection.collector

    def iter_files(self):
        pass

    @property
    def huge(self):
        return self.size > VOLUME_MAX_SIZE

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

    is_dir = False

    @classmethod
    def get_name(cls, relative_path, collection):
        return relative_path.name

    @classmethod
    def build_from_relative_path(cls, relative_path, collection):
        name = cls.get_name(relative_path, collection)
        file = collection.file_class.build_from_path(Path(collection.path, relative_path))
        return cls(file, name, collection, relative_path, file.size, file.sha1)

    def __init__(self, file, name, collection, relative_path, size, value=5, 
                 sha1="", archived_in=[]):
        self.file = file
        super().__init__(name, collection, relative_path, size, value=value, 
                         sha1=sha1)
     
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

    is_dir = True

    @classmethod
    def get_directory_files_data(cls, directory_path, collection):
        "Builds a list of files according the requirements of the collection class"
        files = []
        size = 0
        for dir_path, dir_names, file_names in os.walk(directory_path):
            for file_name in file_names:
                file_path = Path(dir_path, file_name)
                if not collection.validate_file(file_path):
                    continue
                file = collection.file_class.build_from_path(file_path)
                size += file.size
                files.append(file)
        return files, size

    @classmethod
    def build_from_relative_path(cls, relative_path, collection):
        "Builds a DirectoryIteem given its relative path and the belonging collection"
        directory_path = Path(collection.path, relative_path)
        directory_name = relative_path
        files, size = cls.get_directory_files_data(directory_path, collection)
        name = collection.get_item_name_from_path(directory_path)
        return cls(files, name, collection, directory_name, size)

    def __init__(self, files, name, collection, relative_path, size, value=5, 
                 sha1=""):
        super().__init__(name, collection, relative_path, size, value=value, 
                         sha1=sha1)
        self.files = []
        self.sha1_table = ""
        self.sha1 = sha1
        for file in files:
            directory_item_file = DirectoryItemFile.build_from_file(self, file)
            self.files.append(directory_item_file)
        self.files.sort()

    def iter_files(self):
        for f in self.files:
            yield f

    @property
    def hashed(self):
        for file in self.iter_files():
            if file.sha1 == "":
                return False
        return True

    def compute_sha1(self):
        self.sha1_table = "\n".join([str(file) for file in self.files])
        self.sha1 = hashlib.sha1(self.sha1_table.encode("utf-8")).hexdigest()

    def __dict__(self, path):
        return {"name": self.name, "size": self.size,
                "files": [x.__dict__() for x in self.files]}


class Collection:
    """A logical abstraction of all the elements of the same collection.
    Now a directory in the Master directory, but can be in multiples locations
    in the future.

    It should include all the intrinsics of handling the collection, beeing the
    other classes auxiliaries of this one.
    """

    item_class = Item
    file_class = File # You can personalize this object build_from_path to build
                      # sophiticated objects
    
    def __init__(self, relative_path, collector):
        self.collector = collector
        self.relative_path = relative_path
        self.path = Path(collector.path, relative_path)
        self.items = []
        for relative_path in self.path.iterdir():
            item = self.item_class.build_from_relative_path(relative_path, self)
            self.items.append(item)
        self.hashed = False
    
    def iter_items(self):
        for item in self.items:
            yield item

    def iter_files(self):
        for item in self.items:
            for file in item.iter_files():
                yield file
        
    def compute_sha1(self):
        files = list(self.iter_files())
        paths = [x.path for x in files]
        hashes = compute_hashes(paths)
        for file, sha1 in zip(files, hashes):
            file.sha1 = sha1 
        self.hashed = True
        self.update_sha1()

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

    def update_sha1(self):
        for item in self.items:
            item.compute_sha1()


class Collector:
    """The root of the collection system, an object that represents the main directory of the 
    collection"""

    def __init__(self, path):
        self.path = path
        self.collections = []

    def add_collection(self, collection):
        self.collections.append(collection)


def get_parser():
    parser = argparse.ArgumentParser(description="Manages a collection of data")
    subparsers = parser.add_subparsers()
    parser_add = subparsers.add_parser('add', description="adds new content to the collection")

    parser_verify = subparsers.add_parser('verify')
    parser_list_files = subparsers.add_parser('list-files')
    parser_list_files.set_defaults(func=list_files)
    parser_list_items = subparsers.add_parser('list-items')
    parser_list_items.set_defaults(func=list_items)
    parser_dump = subparsers.add_parser('dump')
    parser_resume = subparsers.add_parser('resume')
    return parser


def main():
    # TODO  Fix to support default windows and mac paths
    c = Collection.build_from_files()
    #parser = get_parser()
    #args = parser.parse_args(sys.argv[1:])
    #args.func()
    list_items(c)


if __name__ == "__main__":
    main()
