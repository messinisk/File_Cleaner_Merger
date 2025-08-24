# file_sync_manager.py
import os
import secrets
from typing import List
from pure_core.logfile import LogOpject


class FileMerger:
    """Κλάση για συγχώνευση αρχείων και διαχείριση διπλών."""

    def __init__(self, log_level="info"):
        self.log_level = log_level

    @LogOpject("info")
    def merge_by_version_date(self, file_a: dict, file_b: dict) -> str:
        """Συγχωνεύει δύο αρχεία με βάση την ημερομηνία δημιουργίας τους."""
        created_a = os.path.getctime(file_a["path"])
        created_b = os.path.getctime(file_b["path"])

        base, other = (file_a, file_b) if created_a <= created_b else (file_b, file_a)

        # Αν τα timestamps είναι ίδια, διαλέγουμε file_a ως base
        if created_a == created_b:
            base, other = file_a, file_b

        self._append_content(base["path"], other["path"], "Merged version")
        os.remove(other["path"])

        return f"Συγχωνεύθηκαν εκδόσεις: {other['path']} -> {base['path']}"

    @LogOpject("info")
    def merge_random_conflict(self, file_a: dict, file_b: dict) -> str:
        """Συγχωνεύει δύο αρχεία τυχαία."""
        chosen, discarded = (
            (file_a, file_b) if secrets.choice([True, False]) else (file_b, file_a)
        )

        self._append_content(
            chosen["path"], discarded["path"], "Merged random conflict"
        )
        os.remove(discarded["path"])
        return f"Τυχαία συγχώνευση: {discarded['path']} -> {chosen['path']}"

    @LogOpject("info")
    def delete_duplicates(self, duplicate_files: List[dict]) -> str:
        """Διαγράφει τα διπλά αρχεία, κρατώντας το πρώτο."""
        for dup in duplicate_files[1:]:
            os.remove(dup["path"])
        return f"Διαγράφηκαν {len(duplicate_files) - 1} διπλά"

    def _append_content(self, base_path: str, other_path: str, merge_type: str):
        """Βοηθητική μέθοδος για συγχώνευση περιεχομένου αρχείων."""
        with open(other_path, "r", encoding="utf-8") as f_other:
            content = f_other.read()
        with open(base_path, "a", encoding="utf-8") as f_base:
            f_base.write(f"\n\n# --- {merge_type} ---\n")
            f_base.write(f"# Συγχώνευση από: {os.path.basename(other_path)}\n")
            f_base.write(content)
