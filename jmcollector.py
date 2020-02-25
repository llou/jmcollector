#! /usr/bin/env python
"""
jmcolector
=========

Manages your collection of data.
"""

import sys
import os
import shutil
from subprocess import run, PIPE
from multiprocessing import Pool, cpu_count
from pathlib import Path, PurePosixPath, PurePath
import logging
import argparse
import json
from yaml import load, dump
try:
    from yaml import CLoader as YLoader, CDumper as YDumper
except ImportError:
    from yaml import Loader as YLoader, Dumper as YDumper


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(levelname)s - %(message)s")
ch.setFormatter(formatter)
logger.addHandler(ch)

DIRECTORY_STRUCTURE = {}
VOLUME_MAX_SIZE = 4300 * 1024 * 1024
TAG = ".jmtag"
INFO_PATH = ".jminfo/data.yml"
EXCLUDED_FILES = [TAG]

MAP = {
      "archivo": "PackageItem",
      "audiolibros": "AudioBookItem",
      "certificaciones": "DocumentItem",
      "datos": "PackageItem",
      "flashcards": "FlashCardItem",
      "juegos": "DirectoryItem",
      "repos": "VMSRepositoryItem",
      "scrapbook": "WebPageItem",
      "Photos": "PhotoVideoDumpItem",
      "videos": "VideoItem",
      "wallpapers": "WallpaperItem"
    }


def get_sha1(path):
    p = run(["/usr/bin/sha1sum", path], stdout=PIPE, stderr=PIPE)
    if p.returncode:
        print("Error processing file %s." % path)
        sys.exit(1)
    return p.stdout.decode("utf-8").split(" ")[0]


def compute_hashes(paths):
    with Pool(cpu_count()) as pool:
        return pool.map(get_sha1, paths)


class Tag:
    def __init__(self, path):
        self.path = path


class File:
    @classmethod
    def build_from_path(cls, path):
        path = Path(path)
        size = path.stat().st_size
        return cls(path, size)

    @classmethod
    def validate(cls, path):
        return True

    def __init__(self, path, size, sha1=None, directory=None):
        self.path = path
        self.size = size
        self.sha1 = sha1
        self.directory = directory
        self.dirname = os.path.dirname(path)
        self.basename = os.path.basename(path)

    def set_directory(self, directory):
        self.directory = directory

    def __eq__(self, other):
        return repr(self) == repr(other)

    def __dict__(self):
        return {"path": self.path, "size": self.size, "sha1": self.sha1}

    def __repr__(self):
        if self.sha1 is None:
            return f"<File path:'{self.basename}'>"
        else:
            return f"<File path:'{self.basename}' sha1:'{self.sha1}'>"


class Item:
    is_dir = None

    @classmethod
    def iter_dir(cls, path):
        pass

    @classmethod
    def validate(self, path):
        return True

    def __init__(self, path, size, value=5, archived_in=[]):
        self.path = path
        self.size = size
        self.value = value
        self.archived_in = archived_in

    def iter_files(self):
        pass

    @property
    def huge(self):
        return self.size > BSIZE

    def __repr__(self):
        return f"<{self.__class__.__name__}: '{self.path}'>"


class DirectoryItem(Item):
    content_type = ""
    is_dir = True
    is_categorical = None
    file_class = File

    @classmethod
    def check_dir(cls, dirname, dirs, file):
        return True

    @classmethod
    def iter_container_dir(cls, container_path):
        if not cls.is_categorical:
            for d in container_path.iterdir():
                if d.is_dir():
                    yield cls.build_from_path(d)
        else:
            for dirname, dirs, files in os.walk(container_path):
                if cls.check_dir(dirname, dirs, files):
                    yield cls.build_from_path(dirname)

    @staticmethod
    def read_metadata(path):
        tag_path = PurePath(path, TAGNAME)
        tag_data = YLoader.load(tag_path.read_text)
        info_path = PurePath(path, INFOPATH)
        info_data = json.loads(info_path.read_text)
        return info_data.update(tat_data)

    @classmethod
    def read_files(cls, path):
        files = []
        size = 0
        for dirpath, dirnames, filenames in os.walk(path):
            for fname in filenames:
                if fname in EXCLUDED_FILES:
                    continue
                fpath = os.path.join(dirpath, fname)
                f = cls.file_class.build_from_path(fpath)
                size += f.size
                files.append(f)
        return files, size

    @classmethod
    def build_from_path(cls, path):
        files, size = cls.read_files(path)
        return cls(path, files, size)

    @classmethod
    def build_from_metadata(cls, path):
        metadata = cls.get_metadata(path)
        files = metadata['files']
        size = metadata['size']
        return cls(path, files, size, metadata=metadata)

    def __init__(self, path, files, size, metadata={}):
        super().__init__(path, size)
        self.name = os.path.basename(path)
        for f in files:
            f.set_directory(self)
        self.files = files
        self.size = size
        self.metadata = metadata

    def is_subdir(self, path):
        """
        It is used to avoid repeating directories while crawling for
        collections
        """
        return self.path in path.parents

    def iter_files(self):
        for f in self.files:
            yield f

    def __dict__(self, path):
        return {"name": self.name, "size": self.size,
                "files": [x.__dict__() for x in self.files]}


class FileItem(Item):
    is_dir = False
    file_class = File

    @classmethod
    def iter_container_dir(cls, container_path):
        for dirpath, subdirs, files in os.walk(container_path):
            for f in files:
                file_path = os.path.join(dirpath, f)
                if cls.validate(file_path):
                    yield cls(cls.file_class.build_from_path(file_path))

    def __init__(self, file):
        super().__init__(file.path, file.size)
        self.file = file

    def iter_files(self):
        yield self.file

    def __dict__(self, path):
        return self.file.__dict__()


class VMSRepositoryItem(DirectoryItem):
    """
    Represents the contents of a vms repository.
    """
    is_categorical = False
    content_type = "vms"


class GitRepositoryItem(VMSRepositoryItem):
    """
    Represents the contents of a git repository.
    """
    content_type = "git"


class WebPageItem(DirectoryItem):
    """
    Represents a page download with all of their items, downloaded normally
    with scrapbook.
    """
    is_categorical = False
    content_type = "www"


class PhotoVideoDumpItem(DirectoryItem):
    """
    Represents the directory product of dumping the contents of a camera card.
    """
    is_categorical = False
    content_type = "camera"


class DataItem(DirectoryItem):
    """
    Represents a directory of unrelated sources of information, for feeding
    programs and analysis.
    """
    is_categorical = False
    content_type = "data"


class MusicalRecordItem(DirectoryItem):
    """
    Represents the contents of a record downloaded or ripped into a bunch of
    mp3 or other format.
    """
    is_categorical = False
    content_type = "music"


class AudioBookItem(DirectoryItem):
    """
    Represents the contents of a record downloaded or ripped into a bunch of
    mp3 or other format.
    """
    is_categorical = False
    content_type = "audiobook"


class SerialItem(DirectoryItem):
    """
    Represents the contents of a tv serial or documentary as a colection of
    files
    """
    is_categorical = False
    content_type = "www"


class AssortedCollectionOfUnrelatedCoolStuffItem(DirectoryItem):
    """
    Some directory you found somewhere and didn't want to throw it all away.
    """
    is_categorical = False
    content_type = "cool"


class CourseMaterialsAndExcercisesItem(DirectoryItem):
    """
    Represents the directory that contains resources of a course you did in
    the past.
    """
    is_categorical = False
    content_type = "course"


class FlashCardItem(DirectoryItem):
    """
    A file that contains one or more items, saved or not in other medium, that
    is the container of other collectables.
    """
    is_categorical = True
    content_type = "flashcard"

    @classmethod
    def check_dir(self, dirname, subdirs, files):
        if "flashcard.yml" in files or "flashcard.yaml" in files:
            return True


# File Items


class DocumentItem(FileItem):
    """
    Represents all kind of documents from word files to Autocad ones.
    """
    globs = ["*.pdf"]


class EbookItem(FileItem):
    globs = ["*.epub"]


class VideoItem(FileItem):
    globs = []


class GifItem(VideoItem):
    globs = ["*.gif"]


class MovieItem(VideoItem):
    globs = ["*.mp4"]


class ImageItem(FileItem):
    globs = ["*.jpg", "*.png"]


class WallpaperItem(ImageItem):
    pass


class MemeItem(ImageItem):
    pass


class PhotoItem(ImageItem):
    globs = ["*.jpg", "*.raw"]


class PackageItem(FileItem):
    globs = ["*.zip", "*.tgz", "*.tar.gz"]


class ItemContainer:
    """
    An object that contains items
    """
    pass


class DirectoryContainer(ItemContainer):
    """
    A directory that contains items and can grow with the addition of more
    content.
    """
    pass


class VolumeContainer(ItemContainer):
    """
    A directory, DVD or other media that contains a fixed amount of items.
    """
    content_type = "item"


class Collection:

    @classmethod
    def build_from_files(cls, root_dir, map):
        """
        Given the root of the collection directory and a map with the
        different collectables subdirectories loads this data and verify the
        structure is valid by matching the tag with the map entry, raising an
        error if this is not happening.
        """
        files = []
        result = {}
        root_dir = Path(root_dir)
        if not root_dir.exists():
            raise CollectorError("Invalid collector root dir")
        for path, item_type_name in map.items():
            items_path = root_dir / PurePosixPath(path)
            items_type = globals()[item_type_name]
            items = []
            for item in items_type.iter_container_dir(items_path):
                items.append(item)
                files += [x for x in item.iter_files()]
            result[path] = items
        # Compute hashes
        paths = [f.path for f in files]
        hashes = compute_hashes(paths)
        for hash, file in zip(hashes, files):
            file.sha1 = hash
        return cls(result)

    @classmethod
    def build_from_database(cls):
        """
        Given the connection data to a database  builds the map of the objects
        """
        return map

    @classmethod
    def build_from_dump(cls, path, password):
        """
        Given the path to an encrypted tarball that contains a json file of the
        data objects returns the map.
        """
        return map

    def __init__(self, mapping):
        self.mapping = mapping

    def iter_items(self):
        for name, item_list in self.mapping.items():
            for item in item_list:
                yield item

    def iter_files(self):
        for item in self.iter_items():
            for file in item.iter_files():
                yield file


def list_items():
    c = Collection.build_from_files("/home/llou/Dropbox", MAP)
    for item in c.iter_items():
        print(repr(item))


def list_files():
    c = Collection.build_from_files("/home/llou/Dropbox", MAP)
    for item in c.iter_files():
        print(repr(item))


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
    parser = get_parser()
    args = parser.parse_args(sys.argv[1:])
    args.func()


if __name__ == "__main__":
    main()
