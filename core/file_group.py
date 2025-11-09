from typing import List, Optional

from core import File


class FileGroup:
    """Ομάδα αρχείων που μοιάζουν/πρέπει να συγχωνευτούν."""

    def __init__(self, files: Optional[List[File]] = None):
        self.files: List[File] = files if files else []

    def add_file(self, file: File):
        self.files.append(file)

    def similarity_score(self, other_file):
        if not self.files:
            return 0.0
        # Παράδειγμα: υπολογίζει τη μέση ομοιότητα με τα υπάρχοντα αρχεία
        from core.similarity import FileSimilarity
        sim = FileSimilarity()
        scores = [sim.similarity_score(f.content, other_file.content) for f in self.files]
        return sum(scores) / len(scores)

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
