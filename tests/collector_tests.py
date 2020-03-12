import sys
import unittest
from unittest import mock
from pathlib import Path

TESTDIR = Path(__file__).resolve().parent
ROOTDIR = TESTDIR.parent
PROJECTDIR = Path(ROOTDIR, "jmcollector")
sys.path.insert(0, str(PROJECTDIR))
import jmcollector


TEST_FILE = Path(TESTDIR, "fixtures/text1.txt")
FILE_HASH = "63bbfea82b8880ed33cdb762aa11fab722a90a24"
TEST_FILE2 = Path(TESTDIR, "fixtures/text2.txt")
FILE_HASH2 = "c8358c72121d52860a6652baba4e49a8b3088593"

COLLECTOR_PATH = Path(TESTDIR, "fixtures", "collector")
FILE_COLLECTION_NAME = "file_collection"
DIRECTORY_COLLECTION_NAME = "directory_collection"
DIRECTORY_ITEM_NAME = "directory_collection/record1"


class TestGetHash(unittest.TestCase):
    def test_hash(self):
        self.assertEqual(jmcollector.get_sha1_file(TEST_FILE), FILE_HASH)


class TestFile(unittest.TestCase):
    def test_file(self):
        f = jmcollector.File.build_from_path(TEST_FILE, compute_hash=True)
        self.assertEqual(f.path, TEST_FILE)
        self.assertEqual(f.size, 5)
        self.assertEqual(f.sha1, FILE_HASH)

    def test_dict(self):
        f = jmcollector.File.build_from_path(TEST_FILE, compute_hash=True)
        d = f.__dict__()
        self.assertIn("path", d)
        self.assertEqual(d['path'], str(TEST_FILE))
        self.assertIn("size", d)
        self.assertEqual(d['size'], 5)
        self.assertIn("sha1", d)
        self.assertEqual(d['sha1'], FILE_HASH)

    def test_equality(self):
        f1 = jmcollector.File.build_from_path(TEST_FILE, compute_hash=True)
        f2 = jmcollector.File.build_from_path(TEST_FILE2, compute_hash=True)
        self.assertEqual(f1, f1)
        self.assertNotEqual(f1, f2)
        
class TestDirectoryFile(unittest.TestCase):
    def test_file(self):
        directory_item_mock = mock.Mock()
        directory_item_mock.relative_path = ROOTDIR
        f = jmcollector.File.build_from_path(TEST_FILE, compute_hash=True)
        df = jmcollector.DirectoryItemFile.build_from_file(directory_item_mock, f)
        self.assertEqual(f.path, TEST_FILE)
        self.assertEqual(f.size, 5)
        self.assertEqual(f.sha1, FILE_HASH)

    def test_dict(self):
        directory_item_mock = mock.Mock()
        directory_item_mock.relative_path = ROOTDIR
        f = jmcollector.File.build_from_path(TEST_FILE, compute_hash=True)
        df = jmcollector.DirectoryItemFile.build_from_file(directory_item_mock, f)
        d = df.__dict__()
        self.assertIn("relative_path", d)
        self.assertEqual(d['relative_path'], 'tests/fixtures/text1.txt')
        self.assertIn("size", d)
        self.assertEqual(d['size'], 5)
        self.assertIn("sha1", d)
        self.assertEqual(d['sha1'], FILE_HASH)

    def test_equality(self):
        directory_item_mock = mock.Mock()
        directory_item_mock.relative_path = ROOTDIR
        f1 = jmcollector.File.build_from_path(TEST_FILE, compute_hash=True)
        f2 = jmcollector.File.build_from_path(TEST_FILE2, compute_hash=True)
        df1 = jmcollector.DirectoryItemFile.build_from_file(directory_item_mock, f1)
        df2 = jmcollector.DirectoryItemFile.build_from_file(directory_item_mock, f2)
        self.assertEqual(f1, f1)
        self.assertEqual(df1, df1)
        self.assertNotEqual(f1, f2)
        self.assertNotEqual(df1, df2)

class ItemsTestCase(unittest.TestCase):
    def setUp(self):
        self.collector = jmcollector.Collector(COLLECTOR_PATH)
        self.collection1 = jmcollector.FileCollection(FILE_COLLECTION_NAME, self.collector)
        self.collection2 = jmcollector.DirectoryCollection(DIRECTORY_COLLECTION_NAME, self.collector)

    def test_item(self):
        item = jmcollector.Item("test", self.collection1, 'path', 5, value=7, 
                                sha1=FILE_HASH)
        self.assertEqual(item.name, "test")
        self.assertEqual(item.collection, self.collection1)
        self.assertEqual(str(item.relative_path), "path")
        self.assertEqual(item.size, 5)
        self.assertEqual(item.value, 7)
        self.assertEqual(item.sha1, FILE_HASH)
        self.assertFalse(item.huge)

    def test_items_equal(self):
        item = jmcollector.Item("test", self.collection1, 'path', 5, value=7, 
                                sha1=FILE_HASH)
        item2 = jmcollector.Item("test", self.collection1, 'path', 5, value=7, 
                                sha1=FILE_HASH)
        self.assertEqual(item, item2)
        item3 = jmcollector.Item("test2", self.collection2, "path2", 3, 
                                 value=2, sha1=FILE_HASH2)
        self.assertNotEqual(item, item3)

class FileItemsTestCase(unittest.TestCase):
    def setUp(self):
        self.collector = jmcollector.Collector(COLLECTOR_PATH)
        self.collection1 = jmcollector.FileCollection(FILE_COLLECTION_NAME, self.collector)
        self.file = jmcollector.File.build_from_path(TEST_FILE)
        self.directory_file1 = self.collection1.items[0]
        self.directory_file2 = self.collection1.items[1]

    def test_build_from_relative_path(self):
        pass #  TODO Pending

    def test_file_items(self):
        item = jmcollector.FileItem(self.file, "test", self.collection1, 'path', 
                                    5, value=7, sha1=FILE_HASH)
        self.assertEqual(item.name, "test")
        self.assertEqual(item.collection, self.collection1)
        self.assertEqual(str(item.relative_path), "path")
        self.assertEqual(item.size, 5)
        self.assertEqual(item.value, 7)
        self.assertEqual(item.sha1, FILE_HASH)
        self.assertFalse(item.huge)

    def test_file_items_equal(self):
        self.assertEqual
        
class DirectoryItemTestCase(unittest.TestCase):
    def setUp(self):
        self.collector = jmcollector.Collector(COLLECTOR_PATH)
        self.collection = jmcollector.DirectoryCollection(DIRECTORY_COLLECTION_NAME, 
                                                          self.collector)
        self.record1 = self.collection.items[0]
        self.record2 = self.collection.items[1]
        self.record1_table = """63bea2e3b0c7cd2d1f98bc5b7a9951eafcfead0f track1.mp3
3ee88a74d3722b336a69c428d226f731435c71ba track2.mp3
da39a3ee5e6b4b0d3255bfef95601890afd80709 track3.mp3"""

    def test_get_directory_files_data(self):
        path = self.record1.path
        files, size = jmcollector.DirectoryItem.get_directory_files_data(path, self.collection)
        self.assertEqual(len(files), 3)
        self.assertEqual(size, 11)

    def test_directory_build_from_relative_path(self):
        rf = jmcollector.DirectoryItem.build_from_relative_path(self.record1.path, 
                                                                self.collection)
        self.assertEqual(len(rf.files), 3)
        self.assertEqual(rf.name, "record1")

    def test_item_hash(self):
        self.collection.compute_sha1()
        self.record1.compute_sha1()
        self.assertEqual(self.record1.sha1_table, self.record1_table)


class CollectionTestCase(unittest.TestCase):
    def setUp(self):
        self.collector = jmcollector.Collector(COLLECTOR_PATH)
        self.collection = jmcollector.DirectoryCollection(DIRECTORY_COLLECTION_NAME, 
                                                          self.collector)

    def test_collection(self):
        self.assertEqual(self.collection.collector, self.collector)
        items = list(self.collection.iter_items())
        self.assertEqual(len(items), 2)
        files = list(self.collection.iter_files())
        self.assertEqual(len(files), 6)

    def test_hashes(self):
        self.collection.compute_sha1()
        item1 = self.collection.items[0]
        self.assertEqual(item1.sha1, 'c2f56e617d11664e2e82e78a4558d4bc1308313b')
        item2 = self.collection.items[1]
        self.assertEqual(item2.sha1, 'ab20e03769fbc8f9e0f078a5d7ada798c99d7a45')

class CollectorTestCase(unittest.TestCase):
    pass


class ComputeAlphaTestCase(unittest.TestCase):
    compute_alpha = staticmethod(jmcollector.Item.compute_alpha)

    def test_always_10(self):
        self.assertEqual(self.compute_alpha(10, 10, 10), 1)
        self.assertEqual(self.compute_alpha(10, 5, 10), 1)
        self.assertEqual(self.compute_alpha(10, 7, 10), 1)
        self.assertEqual(self.compute_alpha(10, 3, 10), 1)

    def test_only_1(self):
        self.assertEqual(self.compute_alpha(1, 0, 0), 0.1)
        self.assertEqual(self.compute_alpha(1, 1, 5), 0)
        self.assertEqual(self.compute_alpha(1, 1, 5), 0)
        self.assertEqual(self.compute_alpha(1, 2, 5), 0)
        self.assertEqual(self.compute_alpha(1, 0, 5), 0.1)

    def test_order(self):
        self.assertGreater(self.compute_alpha(10, 0, 0), self.compute_alpha(1, 0, 0))
        self.assertGreater(self.compute_alpha(5, 2, 5), self.compute_alpha(5, 3, 5))
        self.assertGreater(self.compute_alpha(7, 3, 5), self.compute_alpha(5, 3, 5))

if __name__ == "__main__":
    unittest.main()
