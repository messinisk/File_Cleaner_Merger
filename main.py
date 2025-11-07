import os
import difflib
from typing import List, Dict, Optional










# ----------------------------
# Παράδειγμα χρήσης
# ----------------------------

if __name__ == "__main__":
    merger = FileMerger(root_folder="./sample_files")
    merger.scan_files(extensions=[".txt"])
    merger.auto_group()
    results = merger.merge_all()

    for group_name, content in results.items():
        print(f"--- {group_name} ---")
        print(content[:200])  # preview πρώτων 200 χαρακτήρων
        print("...\n")
