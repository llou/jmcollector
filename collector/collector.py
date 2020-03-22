#! /usr/bin/env python
"""
jmcolector
=========

Manages your collection of data.
"""

import sys
import os
from multiprocessing import 
from pathlib import Path
import logging
import argparse
import platform
import json
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
# Constants

DIRECTORY_STRUCTURE = {}
VOLUME_MAX_SIZE = 4300 * 1024 * 1024
TAG = ".jmtag"
INFO_PATH = ".jminfo/data.yml"
EXCLUDED_FILES = [TAG]
MASTER_PATH="~/Dropbox"
COLLECTION_SETTINGS="jmcollector.yml"


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

    def __init__(self, path):
        self.path = path
        self.collections = []

    def iter_items(self):
        for collection in self.collections:
            for item in collection.iter_items(self):
                yield item

    def add_collection(self, collection):
        self.collections.append(collection)


class Volume:
    """Represents a group of items stored in the same removable media, normally
    a disk"""

    @classmethod
    def __init__(self, id, items):
        self.id = id
        self.items = items



