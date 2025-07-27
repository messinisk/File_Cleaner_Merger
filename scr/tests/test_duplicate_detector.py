import os
import shutil
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from duplicate_detector import inspect_directory_state  # type: ignore


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


if __name__ == "__main__":
    unittest.main()
