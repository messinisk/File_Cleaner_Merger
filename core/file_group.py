from typing import List, Optional

from core import File


class FileGroup:
    """Ομάδα αρχείων που μοιάζουν/πρέπει να συγχωνευτούν."""

    def __init__(self, files: Optional[List[File]] = None):
        self.files: List[File] = files if files else []

    def add_file(self, file: File):
        self.files.append(file)

    def similarity_score(self) -> float:
        """Υπολογίζει ένα απλό score βασισμένο σε κοινό περιεχόμενο (προτεινόμενο)."""
        if not self.files:
            return 0.0
        hashes = [f.hash for f in self.files]
        unique_hashes = set(hashes)
        return 1 - len(unique_hashes) / len(hashes)

    def merge(self) -> str:
        """Απλή συγχώνευση περιεχομένου"""
        merged_lines = []
        seen = set()
        for file in self.files:
            for line in file.content.splitlines():
                if line not in seen:
                    merged_lines.append(line)
                    seen.add(line)
        return "\n".join(merged_lines)
