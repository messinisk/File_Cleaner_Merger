import os
import sys
import unittest
from unittest import mock

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from file_sync_manager import delete_duplicates
from file_sync_manager import merge_by_version_date, merge_random_conflict


class TestFileSyncManager(unittest.TestCase):
    def setUp(self):
        patcher1 = mock.patch("os.path.exists", return_value=True)
        patcher2 = mock.patch("os.makedirs")
        patcher3 = mock.patch("os.remove")
        patcher4 = mock.patch("builtins.open", mock.mock_open(read_data="content"))
        patcher5 = mock.patch("os.utime")
        patcher6 = mock.patch("shutil.rmtree")
        self.mock_exists = patcher1.start()
        self.mock_makedirs = patcher2.start()
        self.mock_remove = patcher3.start()
        self.mock_open = patcher4.start()
        self.mock_utime = patcher5.start()
        self.mock_rmtree = patcher6.start()
        self.addCleanup(patcher1.stop)
        self.addCleanup(patcher2.stop)
        self.addCleanup(patcher3.stop)
        self.addCleanup(patcher4.stop)
        self.addCleanup(patcher5.stop)
        self.addCleanup(patcher6.stop)

    def _create_file(self, name, content, created_time=None):
        return {"name": name, "path": f"/fake/{name}"}

    def test_merge_by_version_date(self):
        old_file = self._create_file("file.txt", "Old content")
        new_file = self._create_file("file.txt", "New content")
        merge_by_version_date(old_file, new_file)
        self.mock_open.assert_called()
        self.mock_remove.assert_called()

    def test_merge_random_conflict(self):
        f1 = self._create_file("conflict.txt", "First version")
        f2 = self._create_file("conflict.txt", "Second version")
        merge_random_conflict(f1, f2)
        self.mock_open.assert_called()

    def test_delete_duplicates(self):
        f1 = self._create_file("dup.txt", "Same content")
        f2 = self._create_file("dup.txt", "Same content")
        delete_duplicates([f1, f2])
        self.mock_remove.assert_called()


if __name__ == "__main__":
    unittest.main()