from collections import defaultdict

from duplicate_detector import inspect_directory_state  # type: ignore
from file_sync_manager import delete_duplicates  # type: ignore
from file_sync_manager import merge_by_version_date  # type: ignore
from file_sync_manager import (
    merge_random_conflict,
)  # type: ignore # type: ignore # type: ignore # type: ignore # type: ignore # type: ignore # type: ignore # type: ignore # type: ignore # type: ignore # type: ignore # type: ignore # type: ignore # type: ignore # type: ignore # type: ignore # type: ignore # type: ignore # type: ignore # type: ignore # type: ignore # type: ignore # type: ignore # type: ignore # type: ignore # type: ignore # type: ignore # type: ignore # type: ignore # type: ignore


def process_files(base_path: str):
    file_infos = inspect_directory_state(base_path)  # type: ignore
    if not file_infos:
        print("⚠️ Δεν βρέθηκαν αρχεία προς ανάλυση.")
        return

    grouped_by_name = defaultdict(list)  # type: ignore
    for f in file_infos:  # type: ignore
        grouped_by_name[f["name"]].append(f)  # type: ignore

    for name, files in grouped_by_name.items():  # type: ignore
        if len(files) < 2:  # type: ignore
            continue  # Δεν υπάρχουν διπλότυπα

        # Ομαδοποιήσεις με βάση hash
        hashes = defaultdict(list)  # type: ignore
        for f in files:  # type: ignore
            hashes[f["hash"]].append(f)  # type: ignore

        for group in hashes.values():  # type: ignore
            if len(group) > 1:  # type: ignore
                delete_duplicates(group)

        # Έλεγχος υπόλοιπων για συγχώνευση
        remaining = [f for group in hashes.values() if len(group) == 1 for f in group]  # type: ignore
        while len(remaining) >= 2:  # type: ignore
            f1 = remaining.pop()  # type: ignore
            f2 = remaining.pop()  # type: ignore

            if f1["created"] != f2["created"]:
                # Συγχώνευση με βάση ημερομηνία
                newer = f1 if f1["created"] > f2["created"] else f2  # type: ignore
                older = f2 if newer is f1 else f1  # type: ignore
                merge_by_version_date(older, newer)  # type: ignore
            else:
                # Ίδια ημερομηνία, διαφορετικό περιεχόμενο
                merge_random_conflict(f1, f2)  # type: ignore


if __name__ == "__main__":
    # Δώσε τη διαδρομή του φακέλου που θες να ελέγξεις
    import os

    current_path = os.path.dirname(os.path.abspath(__file__))
    target_path = os.path.join(current_path, "./")
    process_files(target_path)
