import os
import shutil
import stat  # noqa: F401
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from pure_core.duplicate_detector import \
    inspect_directory_state  # type: ignore


class TestDuplicateDetector(unittest.TestCase):
    def setUp(self):
        # Δημιουργούμε προσωρινό φάκελο εργασίας
        self.test_dir = tempfile.mkdtemp()

        # Δημιουργούμε 2 αρχεία με ίδιο όνομα και ίδιο περιεχόμενο
        self.file1 = os.path.join(self.test_dir, "example.txt")
        self.file2 = os.path.join(self.test_dir, "subdir")
        os.makedirs(self.file2)

        self.file2_path = os.path.join(self.file2, "example.txt")

        with open(self.file1, "w") as f:
            f.write("Same content")

        with open(self.file2_path, "w") as f:
            f.write("Same content")

        # Δημιουργούμε 3ο αρχείο με ίδιο όνομα αλλά διαφορετικό περιεχόμενο
        self.diff_dir = os.path.join(self.test_dir, "diff")
        os.makedirs(self.diff_dir)

        self.file3_path = os.path.join(self.diff_dir, "example.txt")
        with open(self.file3_path, "w") as f:
            f.write("Different content")

    def tearDown(self):
        # Καθαρισμός προσωρινών αρχείων
        shutil.rmtree(self.test_dir)

    def test_detect_duplicate_versions(self):
        result = inspect_directory_state(self.test_dir)  # type: ignore
        # Πρέπει να επιστρέφονται 3 αρχεία με το ίδιο όνομα
        matching = [f for f in result if f["name"] == "example.txt"]  # type: ignore
        self.assertEqual(len(matching), 3)  # type: ignore

        # Πρέπει να υπάρχουν τουλάχιστον 2 διαφορετικά hashes
        hashes = {f["hash"] for f in matching}  # type: ignore
        self.assertGreaterEqual(len(hashes), 2)  # type: ignore

    def test_logging_created(self):
        # Ελέγχει αν δημιουργήθηκε log αρχείο
        log_path = "file_inspector.log"
        inspect_directory_state(self.test_dir)
        self.assertTrue(os.path.exists(log_path))

    def test_empty_directory(self):
        empty_dir = tempfile.mkdtemp()
        try:
            result = inspect_directory_state(empty_dir)
            self.assertEqual(result, [])
        finally:
            shutil.rmtree(empty_dir)

    def test_invalid_directory(self):
        result = inspect_directory_state("non_existing_path_123456")
        self.assertEqual(result, [])

    @unittest.skipIf(os.name == "nt", "Windows does not support chmod 000 reliably")
    def test_file_without_permission(self):
        restricted_file = os.path.join(self.test_dir, "restricted.txt")
        with open(restricted_file, "w") as f:
            f.write("Restricted content")

        os.chmod(restricted_file, 0o000)  # Remove all permissions (Unix only)

        try:
            result = inspect_directory_state(self.test_dir)
            self.assertFalse(any(f["path"] == restricted_file for f in result))
        finally:
            os.chmod(restricted_file, 0o644)

    def test_excluded_directory_pycache(self):
        pycache_dir = os.path.join(self.test_dir, "__pycache__")
        os.makedirs(pycache_dir)
        ignored_file = os.path.join(pycache_dir, "ignored.pyc")
        with open(ignored_file, "w") as f:
            f.write("This should be ignored")

        result = inspect_directory_state(self.test_dir)
        self.assertFalse(any("ignored.pyc" in f["path"] for f in result))

    def test_is_system_path_override(self):
        from pure_core.exclusion_config import is_system_path

        # Προσομοιωμένο system path για Linux
        sys_path = "/proc"  # noqa: F841
        if os.name == "nt":
            # Skip test σε Windows
            self.skipTest("System path simulation not reliable on Windows")
        else:
            self.assertTrue(is_system_path("/proc/fake_entry"))
            self.assertFalse(is_system_path("/home/user/project"))

    def test_is_system_path_windows(self):
        from pure_core.exclusion_config import is_system_path

        if os.name != "nt":
            self.skipTest("This test είναι μόνο για Windows")

        self.assertTrue(is_system_path("C:\\Windows\\System32"))
        self.assertTrue(is_system_path("C:\\Program Files\\SomeApp"))
        self.assertTrue(is_system_path("C:\\ProgramData\\config"))
        self.assertFalse(is_system_path("C:\\Users\\User\\Documents\\myproject"))
        self.assertFalse(is_system_path("F:\\clear_file_local\\scr"))


if __name__ == "__main__":
    unittest.main()
