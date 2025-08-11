import os
import shutil
import sys
import tempfile
import unittest
import platform

if platform.system() == "Darwin":
    raise unittest.SkipTest("Skipping all tests on macOS")

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from pure_core.file_sync_manager import delete_duplicates  # type: ignore
from pure_core.file_sync_manager import merge_by_version_date, merge_random_conflict



class TestFileSyncManager(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def _create_file(self, name, content, created_time=None):  # type: ignore
        path = os.path.join(self.test_dir, name)  # type: ignore
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)  # type: ignore
        if created_time:
            # Στα Windows αλλάζει μόνο modification/access time, όχι creation time
            os.utime(path, (created_time, created_time))  # type: ignore
        return {"name": name, "path": path}  # type: ignore

    @unittest.skipIf(os.name == "nt", "Timestamp-based merge not reliable on Windows")
    def test_merge_by_version_date(self):
        path_v1 = os.path.join(self.test_dir, "v1")
        path_v2 = os.path.join(self.test_dir, "v2")
        os.makedirs(path_v1)
        os.makedirs(path_v2)

        old_file = self._create_file(
            "v1/file.txt", "Old content", created_time=1000000000
        )
        new_file = self._create_file(
            "v2/file.txt", "New content", created_time=2000000000
        )

        merge_by_version_date(old_file, new_file)

        self.assertFalse(os.path.exists(new_file["path"]))
        with open(old_file["path"], "r", encoding="utf-8") as f:
            merged = f.read()
            self.assertIn("Old content", merged)
            self.assertIn("New content", merged)
            self.assertIn("# --- Merged version ---", merged)

    def test_merge_random_conflict(self):
        os.makedirs(os.path.join(self.test_dir, "a"))
        os.makedirs(os.path.join(self.test_dir, "b"))

        f1 = self._create_file("a/conflict.txt", "First version")
        f2 = self._create_file("b/conflict.txt", "Second version")

        merge_random_conflict(f1, f2)

        paths = [f1["path"], f2["path"]]
        exists = [os.path.exists(p) for p in paths]
        self.assertEqual(exists.count(True), 1)

        remaining_path = paths[exists.index(True)]
        with open(remaining_path, "r", encoding="utf-8") as f:
            content = f.read()
            self.assertIn("Merged random conflict", content)
            self.assertTrue("First version" in content or "Second version" in content)

    def test_delete_duplicates(self):
        os.makedirs(os.path.join(self.test_dir, "d1"))
        os.makedirs(os.path.join(self.test_dir, "d2"))

        f1 = self._create_file("d1/dup.txt", "Same content")
        f2 = self._create_file("d2/dup.txt", "Same content")

        delete_duplicates([f1, f2])

        files = [f1["path"], f2["path"]]
        existing = [p for p in files if os.path.exists(p)]
        self.assertEqual(len(existing), 1)


if __name__ == "__main__":
    unittest.main()
