# test_file_sync_manager.py
import os
import tempfile
import unittest
from pure_core.file_sync_manager import FileMerger


class TestFileMerger(unittest.TestCase):

    def setUp(self):
        self.merger = FileMerger()
        self.temp_files = []

        # Δημιουργούμε δύο προσωρινά αρχεία
        for i in range(2):
            fd, path = tempfile.mkstemp()
            with os.fdopen(fd, 'w') as tmp:
                tmp.write(f"Content {i}")
            self.temp_files.append({"path": path})

    def tearDown(self):
        # Διαγράφουμε οποιοδήποτε υπόλοιπο αρχείο
        for f in self.temp_files:
            if os.path.exists(f["path"]):
                os.remove(f["path"])

    def test_merge_by_version_date(self):
        result = self.merger.merge_by_version_date(self.temp_files[0], self.temp_files[1])
        self.assertTrue("Συγχωνεύθηκαν εκδόσεις" in result)
        self.assertTrue(os.path.exists(self.temp_files[0]["path"]))
        self.assertFalse(os.path.exists(self.temp_files[1]["path"]))

    def test_merge_random_conflict(self):
        result = self.merger.merge_random_conflict(self.temp_files[0], self.temp_files[1])
        self.assertTrue("Τυχαία συγχώνευση" in result)
        exists_count = sum(os.path.exists(f["path"]) for f in self.temp_files)
        self.assertEqual(exists_count, 1)

    def test_delete_duplicates(self):
        result = self.merger.delete_duplicates(self.temp_files)
        self.assertIn("Διαγράφηκαν 1 διπλά", result)
        self.assertTrue(os.path.exists(self.temp_files[0]["path"]))
        self.assertFalse(os.path.exists(self.temp_files[1]["path"]))


if __name__ == "__main__":
    unittest.main()
