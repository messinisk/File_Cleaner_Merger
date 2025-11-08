import hashlib
import os


class File:
    """Αντικείμενο που αντιπροσωπεύει ένα αρχείο προς συγχώνευση."""

    def __init__(self, path: str):
        self.path = path
        self.name = os.path.basename(path)
        self.size = os.path.getsize(path)
        self.modified_time = os.path.getmtime(path)
        self.content = self._read_content()
        self.hash = self._compute_hash()

    def _read_content(self) -> str:
        try:
            with open(self.path, "r", encoding="utf-8") as f:
                return f.read()
        except Exception:
            return ""

    def _compute_hash(self) -> str:
        return hashlib.sha256(self.content.encode("utf-8")).hexdigest()

    def preview(self, n_lines: int = 10) -> str:
        lines = self.content.splitlines()
        return "\n".join(lines[:n_lines])
