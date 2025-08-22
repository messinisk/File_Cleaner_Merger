import unittest
import os
import re
import platform

# --- Συναρτήσεις υπό δοκιμή ---
def is_excluded_dir(path: str) -> bool:
    pattern = r"(?:__pycache__|__init__\.py|\.git|\.vscode|\.ruff_cache|\.pytest_cache|htmlcov|venv|env|\.mypy_cache|\.idea|node_modules)"
    path_parts = os.path.normpath(path).split(os.sep)
    return any(re.fullmatch(pattern, part) for part in path_parts)

def is_system_path(path: str) -> bool:
    CURRENT_OS = platform.system()
    abs_path = os.path.abspath(path)
    patterns = {
        "Windows": r"^(?:[A-Za-z]:\\Windows|[A-Za-z]:\\Program Files|[A-Za-z]:\\ProgramData)(?:\\|$)",
        "Linux":   r"^(?:/proc|/dev|/sys|/run|/boot)(?:/|$)",
        "Darwin":  r"^(?:/System|/private|/Volumes)(?:/|$)",
        "Android": r"^(?:/proc|/dev|/system|/vendor)(?:/|$)",
    }
    pattern = patterns.get(CURRENT_OS)
    return bool(pattern and re.match(pattern, abs_path))


# --- Tests ---
class TestPathChecks(unittest.TestCase):

    def test_is_excluded_dir_true(self):
        self.assertTrue(is_excluded_dir("project/.git/config"))
        self.assertTrue(is_excluded_dir("/home/user/project/__pycache__/file.py"))
        self.assertTrue(is_excluded_dir("node_modules/package/file.js"))

    def test_is_excluded_dir_false(self):
        self.assertFalse(is_excluded_dir("project/src/module"))
        self.assertFalse(is_excluded_dir("/home/user/project/docs"))

    @unittest.skipUnless(platform.system() == "Linux", "Το τεστ τρέχει μόνο σε Linux")
    def test_is_system_path_linux_true(self):
        self.assertTrue(is_system_path("/proc/cpuinfo"))
        self.assertTrue(is_system_path("/boot/initrd.img"))

    @unittest.skipUnless(platform.system() == "Linux", "Το τεστ τρέχει μόνο σε Linux")
    def test_is_system_path_linux_false(self):
        self.assertFalse(is_system_path("/home/user/file.txt"))
        self.assertFalse(is_system_path("/tmp/data.log"))

    @unittest.skipUnless(platform.system() == "Windows", "Το τεστ τρέχει μόνο σε Windows")
    def test_is_system_path_windows_true(self):
        self.assertTrue(is_system_path(r"C:\Windows\System32"))
        self.assertTrue(is_system_path(r"C:\Program Files\App"))

    @unittest.skipUnless(platform.system() == "Windows", "Το τεστ τρέχει μόνο σε Windows")
    def test_is_system_path_windows_false(self):
        self.assertFalse(is_system_path(r"C:\Users\John\Documents"))
        self.assertFalse(is_system_path(r"D:\Games"))

if __name__ == "__main__":
    unittest.main()
