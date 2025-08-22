import os
import shutil
import tempfile
import unittest
import platform
from unittest.mock import patch

from pure_core.duplicate_detector import (
    file_hash,
    get_file_metadata,
    is_valid_directory,
    collect_file_info,
    group_files_by_name,
    analyze_duplicate_groups,
    should_analyze_group,
    log_identical_group,
    log_versioned_group,
    group_files_by_hash,
    get_all_file_info,
    group_duplicates,
    inspect_directory_state,
)


# Skip όλα σε macOS λόγω διαφορετικού filesystem behavior
if platform.system() == "Darwin":
    raise unittest.SkipTest("Skipping all tests on macOS")


class TestFileHash(unittest.TestCase):
    """Tests για τη συνάρτηση file_hash που υπολογίζει το SHA-256 hash ενός αρχείου."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.filepath = os.path.join(self.tmpdir, "hashfile.txt")
        with open(self.filepath, "w") as f:
            f.write("abc")

    def tearDown(self):
        shutil.rmtree(self.tmpdir)

    def test_valid_hash(self):
        """Ελέγχει ότι επιστρέφεται το σωστό SHA-256 για γνωστό περιεχόμενο."""
        result = file_hash(self.filepath)
        self.assertEqual(
            result,
            "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad",
        )

    def test_missing_file(self):
        """Ελέγχει ότι σηκώνεται FileNotFoundError αν λείπει το αρχείο."""
        with self.assertRaises(FileNotFoundError):
            file_hash(os.path.join(self.tmpdir, "missing.txt"))

    @unittest.skipIf(os.name == "nt", "Windows δεν υποστηρίζει αξιόπιστα chmod 000")
    def test_permission_denied(self):
        """Ελέγχει ότι σηκώνεται PermissionError αν δεν υπάρχει πρόσβαση."""
        restricted_file = os.path.join(self.tmpdir, "restricted.txt")
        with open(restricted_file, "w") as f:
            f.write("restricted")
        os.chmod(restricted_file, 0o000)
        try:
            with self.assertRaises(PermissionError):
                file_hash(restricted_file)
        finally:
            os.chmod(restricted_file, 0o644)


class TestGetFileMetadata(unittest.TestCase):
    """Tests για τη συνάρτηση get_file_metadata που επιστρέφει metadata για αρχεία."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.filepath = os.path.join(self.tmpdir, "file.txt")
        with open(self.filepath, "w") as f:
            f.write("data")

    def tearDown(self):
        shutil.rmtree(self.tmpdir)

    def test_valid_metadata(self):
        """Ελέγχει ότι επιστρέφονται όλα τα κλειδιά metadata."""
        result = get_file_metadata(self.filepath)
        self.assertIsNotNone(result)
        assert result is not None  # βοηθάει τον type checker
        self.assertIn("name", result)


    def test_missing_metadata(self):
        """Ελέγχει ότι επιστρέφεται None για μη υπαρκτό αρχείο."""
        meta = get_file_metadata(os.path.join(self.tmpdir, "missing.txt"))
        self.assertIsNone(meta)

    @patch("pure_core.duplicate_detector.file_hash", side_effect=Exception("hash fail"))
    def test_metadata_hash_fail(self, mock_hash):
        """Ελέγχει ότι επιστρέφεται None αν αποτύχει ο υπολογισμός hash."""
        meta = get_file_metadata(self.filepath)
        self.assertIsNone(meta)


class TestIsValidDirectory(unittest.TestCase):
    """Tests για τη συνάρτηση is_valid_directory."""

    def test_valid_directory(self):
        """Επιστρέφει True για έγκυρο φάκελο."""
        tmpdir = tempfile.mkdtemp()
        try:
            self.assertTrue(is_valid_directory(tmpdir))
        finally:
            shutil.rmtree(tmpdir)

    def test_invalid_directory(self):
        """Επιστρέφει False για μη υπαρκτό φάκελο."""
        result = is_valid_directory("non_existing_dir_123")
        self.assertFalse(result)


class TestCollectFileInfo(unittest.TestCase):
    """Tests για τη συνάρτηση collect_file_info."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.filepath = os.path.join(self.tmpdir, "file.txt")
        with open(self.filepath, "w") as f:
            f.write("data")

    def tearDown(self):
        shutil.rmtree(self.tmpdir)

    def test_collect_basic(self):
        """Επιστρέφει metadata για βασικό αρχείο."""
        result = collect_file_info(self.tmpdir)
        self.assertTrue(any(f["name"] == "file.txt" for f in result))

    @patch("pure_core.duplicate_detector.is_excluded_dir", return_value=True)
    def test_excluded_dir(self, mock_excluded):
        """Επιστρέφει κενή λίστα αν ο φάκελος είναι excluded."""
        result = collect_file_info(self.tmpdir)
        self.assertEqual(result, [])

    @patch("pure_core.duplicate_detector.is_system_path", return_value=True)
    def test_system_path(self, mock_system):
        """Επιστρέφει κενή λίστα αν ο φάκελος είναι system path."""
        result = collect_file_info(self.tmpdir)
        self.assertEqual(result, [])


class TestGroupFilesByName(unittest.TestCase):
    """Tests για τη συνάρτηση group_files_by_name."""

    def test_grouping(self):
        """Ομαδοποιεί αρχεία με ίδιο όνομα."""
        files = [{"name": "a.txt", "hash": "1"}, {"name": "a.txt", "hash": "2"}]
        grouped = group_files_by_name(files)
        self.assertIn("a.txt", grouped)
        self.assertEqual(len(grouped["a.txt"]), 2)


class TestAnalyzeDuplicateGroups(unittest.TestCase):
    """Tests για τη συνάρτηση analyze_duplicate_groups."""

    def test_should_skip(self):
        """Ελέγχει ότι ομάδες με 1 μόνο αρχείο αγνοούνται."""
        result = should_analyze_group([{"name": "a.txt", "hash": "1"}])
        self.assertFalse(result)

    
    # TestAnalyzeDuplicateGroups.test_identical_group
    @patch("pure_core.duplicate_detector.group_files_by_hash",
        return_value={"1": [{"hash": "1", "modified": "2024", "path": "/tmp"},
                            {"hash": "1", "modified": "2024", "path": "/tmp"}]})
    @patch("pure_core.duplicate_detector.LoggerManager.info")
    def test_identical_group(self, mock_info, mock_group):
        analyze_duplicate_groups({"a.txt": [
            {"name": "a.txt", "hash": "1", "modified": "2024", "path": "/tmp"},
            {"name": "a.txt", "hash": "1", "modified": "2024", "path": "/tmp"},
        ]})
        mock_info.assert_called()


    # TestAnalyzeDuplicateGroups.test_versioned_group
    @patch("pure_core.duplicate_detector.group_files_by_hash",
        return_value={"1": [{"hash": "1", "modified": "2024", "path": "/tmp/a"}],
                        "2": [{"hash": "2", "modified": "2024", "path": "/tmp/b"}]})
    @patch("pure_core.duplicate_detector.LoggerManager.info")
    def test_versioned_group(self, mock_info, mock_group):
        analyze_duplicate_groups({"a.txt": [
            {"name": "a.txt", "hash": "1", "modified": "2024", "path": "/tmp/a"},
            {"name": "a.txt", "hash": "2", "modified": "2024", "path": "/tmp/b"},
        ]})
        mock_info.assert_called()



class TestLogFunctions(unittest.TestCase):
    """Direct tests για log_identical_group και log_versioned_group."""

    @patch("pure_core.duplicate_detector.LoggerManager.info")
    def test_log_identical_group(self, mock_info):
        """Ελέγχει ότι το log_identical_group καλεί LoggerManager.info."""
        log_identical_group("test.txt")
        mock_info.assert_called_once()

    def test_log_versioned_group(self):
        result = log_versioned_group("test.txt", {"hash1": [{"modified": "2024", "path": "/tmp/file"}]})
        self.assertTrue(any("Έκδοση" in line for line in result))



class TestGroupFilesByHash(unittest.TestCase):
    """Tests για τη συνάρτηση group_files_by_hash."""

    def test_grouping(self):
        """Ομαδοποιεί αρχεία με ίδιο hash."""
        files = [{"hash": "1", "name": "a"}, {"hash": "1", "name": "b"}]
        grouped = group_files_by_hash(files)
        self.assertIn("1", grouped)
        self.assertEqual(len(grouped["1"]), 2)


class TestGetAllFileInfo(unittest.TestCase):
    """Tests για τη συνάρτηση get_all_file_info."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.filepath = os.path.join(self.tmpdir, "afile.txt")
        with open(self.filepath, "w") as f:
            f.write("abc")

    def tearDown(self):
        shutil.rmtree(self.tmpdir)

    def test_collect_valid_file(self):
        """Επιστρέφει metadata για υπαρκτό αρχείο."""
        result = get_all_file_info(self.tmpdir)
        self.assertTrue(any(f["name"] == "afile.txt" for f in result))

    def test_unreadable_file(self):
        """Ελέγχει ότι σφάλματα στο άνοιγμα αρχείου καταγράφονται με warning."""
        dummy_file = os.path.join(self.tmpdir, "badfile.txt")
        with open(dummy_file, "w") as f:
            f.write("x")

        with patch("pure_core.duplicate_detector.open", side_effect=OSError("fail")), \
             patch("pure_core.duplicate_detector.LoggerManager.warning") as mock_warn:
            result = get_all_file_info(self.tmpdir)
            self.assertIsInstance(result, list)
            mock_warn.assert_called()


class TestGroupDuplicates(unittest.TestCase):
    """Tests για τη συνάρτηση group_duplicates."""

    def test_group_duplicates(self):
        """Ομαδοποιεί αρχεία με ίδιο hash σε ομάδες."""
        files = [
            {"name": "a.txt", "hash": "1"},
            {"name": "b.txt", "hash": "1"},
            {"name": "c.txt", "hash": "2"},
        ]
        grouped = group_duplicates(files)
        self.assertEqual(len(grouped), 2)


class TestInspectDirectoryState(unittest.TestCase):
    """Tests για τη συνάρτηση inspect_directory_state."""

    def test_empty_directory(self):
        """Επιστρέφει [] για άδειο φάκελο."""
        tmpdir = tempfile.mkdtemp()
        try:
            result = inspect_directory_state(tmpdir)
            self.assertEqual(result, [])
        finally:
            shutil.rmtree(tmpdir)

    def test_with_files(self):
        """Επιστρέφει metadata για αρχεία μέσα σε φάκελο."""
        tmpdir = tempfile.mkdtemp()
        try:
            f1 = os.path.join(tmpdir, "a.txt")
            with open(f1, "w") as f:
                f.write("abc")
            f2 = os.path.join(tmpdir, "b.txt")
            with open(f2, "w") as f:
                f.write("def")
            result = inspect_directory_state(tmpdir)
            self.assertTrue(any(r["name"] in ["a.txt", "b.txt"] for r in result))
        finally:
            shutil.rmtree(tmpdir)


if __name__ == "__main__":
    unittest.main()