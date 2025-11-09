from unittest.mock import MagicMock, patch
from core import File, FileGroup, FileMerger


def test_init_creates_empty_collections():
    merger = FileMerger("test_data")

    assert merger.root_folder == "test_data"
    assert merger.files == []
    assert merger.groups == []


def test_merge_combines_unique_lines():
    f1 = MagicMock(content="a\nb\nc")
    f2 = MagicMock(content="b\nc\nd")
    group = FileGroup(files=[f1, f2])
    result = group.merge()
    assert result == "a\nb\nc\nd"

def test_merge_empty_group():
    group = FileGroup(files=[])
    assert group.merge() == ""

def test_scan_files_filters_and_adds_files():
    merger = FileMerger("dummy_folder")

    fake_walk = [
        ("dummy_folder", [], ["a.txt", "b.csv", "c.md"]),
    ]
    fake_file_obj = MagicMock()

    with patch("core.file_merger.os.walk", return_value=fake_walk) as mock_walk, \
         patch("core.file_merger.File", return_value=fake_file_obj):

        merger.scan_files(extensions=[".txt", ".md"])

        # ✅ Ελέγχουμε ότι η os.walk κλήθηκε με το σωστό path
        mock_walk.assert_called_once_with("dummy_folder")

    # ✅ Ελέγχουμε ότι δημιουργήθηκαν File αντικείμενα ΜΟΝΟ για .txt και .md
    assert len(merger.files) == 2
    assert all(f == fake_file_obj for f in merger.files)

def test_auto_group_empty():
    merger = FileMerger("dummy_folder")
    merger.files = []
    merger.auto_group()
    assert merger.groups == []

def test_auto_group_duplicate_hashes():
    file1 = MagicMock(hash="abc")
    file2 = MagicMock(hash="abc")

    merger = FileMerger("dummy_folder")
    merger.files = [file1, file2]
    merger.auto_group()

    assert len(merger.groups) == 1
    assert merger.groups[0].files == [file1, file2]

def test_merge_all_empty_groups():
    merger = FileMerger("dummy_folder")
    merger.groups = []
    result = merger.merge_all()
    assert result == {}  # επιστρέφει κενό dict

def test_merge_all_single_group():
    file1 = MagicMock()
    file1.content = "a\nb\nc"

    group = FileGroup(files=[file1])
    merger = FileMerger("dummy_folder")
    merger.groups = [group]

    result = merger.merge_all()
    assert result == {"group_1": "a\nb\nc"}

def test_merge_all_multiple_groups():
    file1 = MagicMock()
    file1.content = "a\nb\nc"
    file2 = MagicMock()
    file2.content = "d\ne"

    group1 = FileGroup(files=[file1])
    group2 = FileGroup(files=[file2])

    merger = FileMerger("dummy_folder")
    merger.groups = [group1, group2]

    result = merger.merge_all()
    assert result == {
        "group_1": "a\nb\nc",
        "group_2": "d\ne"
    }

