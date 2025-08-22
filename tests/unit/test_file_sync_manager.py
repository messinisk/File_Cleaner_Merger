import os
import sys
import tempfile
import secrets
import unittest
import platform
import shutil

if platform.system() == "Darwin":
    raise unittest.SkipTest("Skipping all tests on macOS")

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from pure_core.file_sync_manager import delete_duplicates  # type: ignore
from pure_core.file_sync_manager import merge_by_version_date, merge_random_conflict  # noqa: F401



class TestMergeFiles(unittest.TestCase):

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        # Καθαρισμός αρχείων
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def _create_file(self, path, content, created_time=None):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        if created_time:
            os.utime(path, (created_time, created_time))
        return {"path": path}

    def test_merge_by_version_date(self):
        old_path = os.path.join(self.test_dir, "v1", "file.txt")
        new_path = os.path.join(self.test_dir, "v2", "file.txt")

        old_file = self._create_file(old_path, "Old content", created_time=1000000000)
        new_file = self._create_file(new_path, "New content", created_time=2000000000)

        result = merge_by_version_date(old_file, new_file)

        # Έλεγχοι
        self.assertIn("Συγχωνεύθηκαν εκδόσεις", result)
        self.assertFalse(os.path.exists(new_path))

        with open(old_path, "r", encoding="utf-8") as f:
            merged = f.read()
            self.assertIn("Old content", merged)
            self.assertIn("New content", merged)
            self.assertIn("# --- Merged version ---", merged)

    def test_merge_same_timestamp(self):
        # Edge case: ίδια timestamp
        path1 = os.path.join(self.test_dir, "file1.txt")
        path2 = os.path.join(self.test_dir, "file2.txt")

        f1 = self._create_file(path1, "A", created_time=1234567890)
        f2 = self._create_file(path2, "B", created_time=1234567890)

        result = merge_by_version_date(f1, f2)  # noqa: F841

        self.assertTrue(os.path.exists(path1))
        self.assertFalse(os.path.exists(path2))
        with open(path1, "r", encoding="utf-8") as f:
            merged = f.read()
            self.assertIn("A", merged)
            self.assertIn("B", merged)


class TestRandomMergeAndDelete(unittest.TestCase):

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        # Καθαρισμός αρχείων
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
        
    def _create_file(self, path, content):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        return {"path": path}

    def test_merge_random_conflict(self):
        file1_path = os.path.join(self.test_dir, "file1.txt")
        file2_path = os.path.join(self.test_dir, "file2.txt")

        file1 = self._create_file(file1_path, "Content A")
        file2 = self._create_file(file2_path, "Content B")

        # Patch του secrets.choice για deterministic test
        original_choice = secrets.choice
        secrets.choice = lambda x: True  # Επιλέγει πάντα file_a ως chosen
        try:
            result = merge_random_conflict(file1, file2)
            # Το file2 διαγράφεται
            self.assertFalse(os.path.exists(file2_path))
            self.assertTrue(os.path.exists(file1_path))

            with open(file1_path, "r", encoding="utf-8") as f:
                merged = f.read()
                self.assertIn("Content A", merged)
                self.assertIn("Content B", merged)
                self.assertIn("# --- Merged random conflict ---", merged)

            self.assertIn("Τυχαία συγχώνευση", result)
        finally:
            secrets.choice = original_choice


    def test_delete_duplicates(self):
        paths = [os.path.join(self.test_dir, f"file{i}.txt") for i in range(3)]
        files = [self._create_file(p, f"Content {i}") for i, p in enumerate(paths)]

        result = delete_duplicates(files)

        # Το πρώτο αρχείο παραμένει
        self.assertTrue(os.path.exists(paths[0]))
        # Τα υπόλοιπα διαγράφονται
        self.assertFalse(os.path.exists(paths[1]))
        self.assertFalse(os.path.exists(paths[2]))

        self.assertEqual(result, "Διαγράφηκαν 2 διπλά")


if __name__ == "__main__":
    unittest.main()
