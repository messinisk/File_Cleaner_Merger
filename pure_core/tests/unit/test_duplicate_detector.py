import os
from pure_core.duplicate_detector import FileMetadata, FileScanner, DuplicateAnalyzer, DuplicateDetector

def create_temp_file(tmpdir, name, content):
    path = os.path.join(tmpdir, name)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    return path

def test_filemetadata_hash_and_dict(tmp_path):
    fpath = create_temp_file(tmp_path, "test.txt", "hello world")
    meta = FileMetadata(fpath)
    assert meta.name == "test.txt"
    assert "hash" in meta.to_dict()
    assert meta.is_same_content(FileMetadata(fpath))

def test_scanner_collect(tmp_path):
    f1 = create_temp_file(tmp_path, "a.txt", "data")  # noqa: F841
    f2 = create_temp_file(tmp_path, "b.csv", "other")  # noqa: F841

    scanner = FileScanner()
    files = scanner.collect(str(tmp_path))
    names = [f.name for f in files]
    assert "a.txt" in names
    assert "b.csv" in names


def test_analyzer_duplicates(tmp_path):
    f1 = create_temp_file(tmp_path, "dup.txt", "same")
    f2 = create_temp_file(tmp_path, "dup.txt", "same")
    files = [FileMetadata(f1), FileMetadata(f2)]
    analyzer = DuplicateAnalyzer()
    result = analyzer.analyze(files)
    assert any("ίδιο περιεχόμενο" in msg for msg in result)

def test_analyzer_versions(tmp_path):
    dir1 = tmp_path / "d1"
    dir2 = tmp_path / "d2"
    dir1.mkdir()
    dir2.mkdir()
    f1 = create_temp_file(dir1, "vers.txt", "v1")
    f2 = create_temp_file(dir2, "vers.txt", "v2")
    files = [FileMetadata(f1), FileMetadata(f2)]
    analyzer = DuplicateAnalyzer()
    result = analyzer.analyze(files)
    assert any("διαφορετικές εκδόσεις" in msg for msg in result), result


def test_detector_integration(tmp_path):
    create_temp_file(tmp_path, "a.txt", "same")
    create_temp_file(tmp_path, "a.txt", "same")
    detector = DuplicateDetector()
    results = detector.inspect(str(tmp_path))
    assert isinstance(results, list)
    assert all("name" in r for r in results)
