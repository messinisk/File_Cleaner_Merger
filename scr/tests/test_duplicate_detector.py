import os
import sys
import unittest
from unittest import mock

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from duplicate_detector import inspect_directory_state  # type: ignore  # noqa: F401

class TestDuplicateDetector(unittest.TestCase):
    def setUp(self):
        patcher1 = mock.patch("os.makedirs")
        patcher2 = mock.patch("builtins.open", mock.mock_open(read_data="Same content"))
        patcher3 = mock.patch("shutil.rmtree")
        patcher4 = mock.patch("os.path.exists", return_value=True)
        patcher5 = mock.patch("os.chmod")
        patcher6 = mock.patch("os.path.join", side_effect=lambda *args: "/".join(args))
        patcher7 = mock.patch("tempfile.mkdtemp", return_value="/tmp/fake_dir")
        self.mock_makedirs = patcher1.start()
        self.mock_open = patcher2.start()
        self.mock_rmtree = patcher3.start()
        self.mock_exists = patcher4.start()
        self.mock_chmod = patcher5.start()
        self.mock_join = patcher6.start()
        self.mock_mkdtemp = patcher7.start()
        self.addCleanup(patcher1.stop)
        self.addCleanup(patcher2.stop)
        self.addCleanup(patcher3.stop)
        self.addCleanup(patcher4.stop)
        self.addCleanup(patcher5.stop)
        self.addCleanup(patcher6.stop)
        self.addCleanup(patcher7.stop)
        # Δημιουργούμε ψεύτικα paths για τα tests
        self.test_dir = "/tmp/fake_dir"
        self.file1 = "/tmp/fake_dir/example.txt"
        self.file2 = "/tmp/fake_dir/subdir"
        self.file2_path = "/tmp/fake_dir/subdir/example.txt"
        self.diff_dir = "/tmp/fake_dir/diff"
        self.file3_path = "/tmp/fake_dir/diff/example.txt"

    def tearDown(self):
        pass  # Όλα τα mocks καθαρίζονται αυτόματα

    # Τα tests παραμένουν ίδια, απλά τώρα δεν αγγίζουν το filesystem

if __name__ == "__main__":
    unittest.main()