"""
duplicate_detector.py
Ανίχνευση διπλοτύπων αρχείων σε φακέλους με αντικειμενοστρεφή αρχιτεκτονική.
"""

import os
import hashlib
from collections import defaultdict
from datetime import datetime
from typing import Optional

from pure_core.logfile import LoggerManager, LogOpject
from pure_core.exclusion_config import is_excluded_dir, is_system_path


ALLOWED_EXTENSIONS = {
    ".txt",
    ".csv",
    ".xlsx",
    ".docx",
    ".pptx",
    ".pdf",
    ".odt",
    ".ods",
    ".odp",
}


class FileMetadata:
    """Αντιπροσωπεύει τα μεταδεδομένα ενός αρχείου."""

    def __init__(self, path: str):
        self.path = os.path.abspath(path)
        self.name = os.path.basename(path)
        self.hash = self._compute_hash()
        st = os.stat(path)
        self.created = datetime.fromtimestamp(st.st_ctime)
        self.modified = datetime.fromtimestamp(st.st_mtime)

    def _compute_hash(self) -> str:
        hasher = hashlib.sha256()
        with open(self.path, "rb") as f:
            while chunk := f.read(8192):
                hasher.update(chunk)
        return hasher.hexdigest()

    def is_same_content(self, other: "FileMetadata") -> bool:
        return self.hash == other.hash

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "path": self.path,
            "hash": self.hash,
            "created": self.created,
            "modified": self.modified,
        }


class FileScanner:
    """Σαρώνει φακέλους και δημιουργεί FileMetadata objects."""

    def __init__(self, allowed_ext: set[str] = ALLOWED_EXTENSIONS):
        self.allowed_ext = allowed_ext

    def is_allowed_file(self, filename: str) -> bool:
        ext = os.path.splitext(filename)[1].lower()
        return ext in self.allowed_ext

    def is_hidden_or_system_file(self, filename: str) -> bool:
        return filename.startswith(".") or filename.lower() in {
            "desktop.ini",
            "thumbs.db",
        }

    @LogOpject("warning")
    def get_file_metadata(self, path: str) -> Optional[FileMetadata]:
        try:
            return FileMetadata(path)
        except Exception as e:
            LoggerManager.warning(f"Αδυναμία ανάγνωσης metadata για '{path}': {e}")
            return None

    def collect(self, base_path: str) -> list[FileMetadata]:
        files: list[FileMetadata] = []
        for root, _, fnames in os.walk(base_path):
            if is_excluded_dir(root) or is_system_path(root):
                continue
            for fname in fnames:
                if not self.is_allowed_file(fname):
                    continue
                if self.is_hidden_or_system_file(fname):
                    continue
                full_path = os.path.join(root, fname)
                metadata = self.get_file_metadata(full_path)
                if metadata:
                    files.append(metadata)
        return files


class DuplicateAnalyzer:
    """Αναλύει διπλότυπα αρχεία."""

    def group_by_name(self, files: list[FileMetadata]) -> dict[str, list[FileMetadata]]:
        grouped = defaultdict(list)
        for f in files:
            grouped[f.name].append(f)
        return grouped

    def group_by_hash(self, files: list[FileMetadata]) -> dict[str, list[FileMetadata]]:
        grouped = defaultdict(list)
        for f in files:
            grouped[f.hash].append(f)
        return grouped

    @LogOpject("info")
    def analyze(self, files: list[FileMetadata]) -> list[str]:
        output: list[str] = []
        name_groups = self.group_by_name(files)
        for name, group in name_groups.items():
            if len(group) <= 1:
                continue
            hash_groups = self.group_by_hash(group)
            if len(hash_groups) == 1:
                msg = f"Αρχείο '{name}' έχει ίδιο περιεχόμενο σε όλες τις τοποθεσίες."
                LoggerManager.info(msg)
                output.append(msg)
            else:
                msg = f"Αρχείο '{name}' έχει διαφορετικές εκδόσεις"
                LoggerManager.info(msg)
                output.append(msg)
                for h, version_files in hash_groups.items():
                    for vf in version_files:
                        detail = f"  - {vf.path} ({vf.modified}) [{h[:10]}]"
                        output.append(detail)
                        LoggerManager.info(detail)

        return output


class DuplicateDetector:
    """Facade class: ενώνει Scanner και Analyzer."""

    def __init__(self, allowed_ext: set[str] = ALLOWED_EXTENSIONS):
        self.scanner = FileScanner(allowed_ext)
        self.analyzer = DuplicateAnalyzer()

    @LogOpject("info")
    def inspect(self, base_path: str) -> list[dict]:
        if not os.path.isdir(base_path):
            LoggerManager.error(f"Μη έγκυρος φάκελος: {base_path}")
            return []
        files = self.scanner.collect(base_path)
        self.analyzer.analyze(files)
        return [f.to_dict() for f in files]
