from unittest.mock import mock_open, patch
from core.file import File
import unittest

@patch("os.path.getsize", return_value=123)
@patch("os.path.getmtime", return_value=1700000000.0)
def test_read_content_success(mock_mtime, mock_getsize):
    fake_data = "some text"
    with patch("builtins.open", mock_open(read_data=fake_data)):
        f = File("fake.txt")
        result = f._read_content()
        assert result == fake_data

@patch("os.path.getsize", return_value=123)
@patch("os.path.getmtime", return_value=1700000000.0)
def test_read_content_failure(mock_mtime, mock_getsize):
    with patch("builtins.open", side_effect=Exception("File error")):
        f = File("missing.txt")
        result = f._read_content()
        assert result == ""

def test_preview_returns_first_lines(tmp_path):
    # Δημιουργούμε προσωρινό αρχείο με 15 γραμμές
    fpath = tmp_path / "example.txt"
    fpath.write_text("\n".join([f"line {i}" for i in range(15)]))

    from core.file import File
    f = File(str(fpath))

    preview_text = f.preview(5)
    lines = preview_text.split("\n")

    assert len(lines) == 5
    assert lines[0] == "line 0"
    assert lines[-1] == "line 4"



if __name__ == "__main__":
    unittest.main()
# tests/test_file.py