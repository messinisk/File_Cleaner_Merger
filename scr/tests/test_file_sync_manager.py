import os
import shutil
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from file_sync_manager import (
    delete_duplicates,  # type: ignore
    merge_by_version_date,
    merge_random_conflict,
)


class TestFileSyncManager(unittest.TestCase):
    def setUp(self):
        # Δημιουργεί προσωρινό φάκελο για κάθε test
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        # Καθαρίζει τον προσωρινό φάκελο μετά από κάθε test
        shutil.rmtree(self.test_dir)

    def _create_file(self, name, content, created_time=None):  # type: ignore
        """Βοηθητική για δημιουργία αρχείων"""
        path = os.path.join(self.test_dir, name)  # type: ignore
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)  # type: ignore
        if created_time:
            os.utime(path, (created_time, created_time))  # type: ignore # τροποποιεί create/modify time
        return {"name": name, "path": path}  # type: ignore

    def test_merge_by_version_date(self):
        path_v1 = os.path.join(self.test_dir, "v1")
        path_v2 = os.path.join(self.test_dir, "v2")
        os.makedirs(path_v1)
        os.makedirs(path_v2)

        old_file = self._create_file(
            "v1/file.txt", "Old content", created_time=1000000000
        )  # type: ignore
        new_file = self._create_file(
            "v2/file.txt", "New content", created_time=2000000000
        )  # type: ignore

        merge_by_version_date(old_file, new_file)

        self.assertFalse(os.path.exists(new_file["path"]))  # type: ignore

        with open(old_file["path"], "r", encoding="utf-8") as f:  # type: ignore
            merged = f.read()
            self.assertIn("Old content", merged)
            self.assertIn("New content", merged)
            self.assertIn("# --- Merged version ---", merged)

    def test_merge_random_conflict(self):
        os.makedirs(os.path.join(self.test_dir, "a"))
        os.makedirs(os.path.join(self.test_dir, "b"))

        f1 = self._create_file("a/conflict.txt", "First version")  # type: ignore
        f2 = self._create_file("b/conflict.txt", "Second version")  # type: ignore

        merge_random_conflict(f1, f2)

        paths = [f1["path"], f2["path"]]  # type: ignore
        exists = [os.path.exists(p) for p in paths]  # type: ignore
        self.assertEqual(exists.count(True), 1)

        remaining_path = paths[exists.index(True)]  # type: ignore
        with open(remaining_path, "r", encoding="utf-8") as f:  # type: ignore
            content = f.read()
            self.assertIn("Merged random conflict", content)
            self.assertTrue("First version" in content or "Second version" in content)

    def test_delete_duplicates(self):
        os.makedirs(os.path.join(self.test_dir, "d1"))
        os.makedirs(os.path.join(self.test_dir, "d2"))

        f1 = self._create_file("d1/dup.txt", "Same content")  # type: ignore
        f2 = self._create_file("d2/dup.txt", "Same content")  # type: ignore

        delete_duplicates([f1, f2])

        files = [f1["path"], f2["path"]]  # type: ignore
        existing = [p for p in files if os.path.exists(p)]  # type: ignore
        self.assertEqual(len(existing), 1)  # type: ignore


if __name__ == "__main__":
    unittest.main()
