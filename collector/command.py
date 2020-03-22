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
