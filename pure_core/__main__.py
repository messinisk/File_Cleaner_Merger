from collections import defaultdict

from pure_core.duplicate_detector import inspect_directory_state
from pure_core.file_sync_manager import (
    delete_duplicates,
    merge_by_version_date,
    merge_random_conflict,
)


def group_files_by_name(file_infos):
    grouped = defaultdict(list)
    for f in file_infos:
        grouped[f["name"]].append(f)
    return grouped


def group_files_by_hash(files):
    grouped = defaultdict(list)
    for f in files:
        grouped[f["hash"]].append(f)
    return grouped


def handle_duplicates(hashes):
    for group in hashes.values():
        if len(group) > 1:
            delete_duplicates(group)


def handle_merges(hashes):
    remaining = [f for group in hashes.values() if len(group) == 1 for f in group]
    while len(remaining) >= 2:
        f1 = remaining.pop()
        f2 = remaining.pop()
        if f1["created"] != f2["created"]:
            newer = f1 if f1["created"] > f2["created"] else f2
            older = f2 if newer is f1 else f1
            merge_by_version_date(older, newer)
        else:
            merge_random_conflict(f1, f2)


def process_files(base_path: str):
    file_infos = inspect_directory_state(base_path)
    if not file_infos:
        print("⚠️ Δεν βρέθηκαν αρχεία προς ανάλυση.")
        return

    grouped_by_name = group_files_by_name(file_infos)

    for name, files in grouped_by_name.items():
        if len(files) < 2:
            continue

        hashes = group_files_by_hash(files)
        handle_duplicates(hashes)
        handle_merges(hashes)


if __name__ == "__main__":
    import os

    current_path = os.path.dirname(os.path.abspath(__file__))
    target_path = os.path.join(current_path, "./")
    process_files(target_path)
