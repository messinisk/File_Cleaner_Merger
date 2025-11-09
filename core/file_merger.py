import os
from typing import Dict, List, Optional

from core import File, FileGroup


class FileMerger:
    """Κύρια κλάση διαχείρισης αρχείων και συγχώνευσης."""

    def __init__(self, root_folder: str):
        self.root_folder = root_folder
        self.files: List[File] = []
        self.groups: List[FileGroup] = []

    def scan_files(self, extensions: Optional[List[str]] = None):
        """Σαρώση φακέλου και δημιουργία File objects"""
        for dirpath, _, filenames in os.walk(self.root_folder):
            for f in filenames:
                if extensions and not any(f.endswith(ext) for ext in extensions):
                    continue
                path = os.path.join(dirpath, f)
                self.files.append(File(path))

    def auto_group(self):
        """Απλό grouping βασισμένο σε hash ταυτότητας"""
        hash_map: Dict[str, FileGroup] = {}
        
        for file in self.files:
            if file.hash in hash_map:
                hash_map[file.hash].add_file(file)
            else:
                hash_map[file.hash] = FileGroup([file])
        
        self.groups = list(hash_map.values())


    def merge_all(self) -> Dict[str, str]:
        """Επιστρέφει ένα dictionary με το όνομα ομάδας και το merged περιεχόμενο"""
        merged_dict = {}
        for i, group in enumerate(self.groups, start=1):
            merged_content = group.merge()
            merged_dict[f"group_{i}"] = merged_content
        return merged_dict
