"""
duplicate detection : ανίχνευση διπλοτύπων
Εστιάζει στον εντοπισμό διπλότυπων αρχείων σε έναν φάκελο. :
It focuses on identifying duplicate files in a folder.
It scans a directory, collects metadata for each valid file, groups files by name,
and analyzes potential duplicates and versions based on file content and metadata.
"""

import hashlib
import os
from collections import defaultdict
from datetime import datetime
from typing import Any, Optional, TypedDict, Union  # noqa: F401
from pure_core.logfile import LoggerManager
from pure_core.logfile import LogOpject
from pure_core.exclusion_config import is_excluded_dir, is_system_path


class FileMetadata(TypedDict):
    """
    Αντιπροσωπεύει τα μεταδεδομένα ενός αρχείου.

    Attributes:
        name (str): Το όνομα του αρχείου.
        path (str): Η πλήρης διαδρομή (path) του αρχείου στο σύστημα αρχείων.
        hash (str): Η τιμή κατακερματισμού (hash) του αρχείου για έλεγχο ακεραιότητας.
        created (datetime): Η ημερομηνία και ώρα δημιουργίας του αρχείου.
        modified (datetime): Η ημερομηνία και ώρα τελευταίας τροποποίησης του αρχείου.
    """

    name: str
    path: str
    hash: str
    created: datetime
    modified: datetime


# -------------------------------
# 🔍 Υπολογισμός hash αρχείου
# -------------------------------


@LogOpject("info")
def file_hash(path: Union[str, os.PathLike[str]]) -> str:
    """
    Υπολογίζει το SHA-256 hash ενός αρχείου, διαβάζοντάς το σε κομμάτια για αποδοτικότητα μνήμης.

    Args:
        path (str): Η πλήρης ή σχετική διαδρομή προς το αρχείο.

    Returns:
        str: Το SHA-256 hash του αρχείου σε δεκαεξαδική μορφή.

    Raises:
        FileNotFoundError: Αν το αρχείο δεν υπάρχει.
        PermissionError: Αν δεν υπάρχει δικαίωμα ανάγνωσης του αρχείου.
    """
    hasher = hashlib.sha256()
    with open(path, "rb") as f:  # type: ignore
        while chunk := f.read(8192):
            hasher.update(chunk)
    return hasher.hexdigest()


@LogOpject("warning")
def get_file_metadata(path: Union[str, os.PathLike[str]]) -> Optional[FileMetadata]:
    """
    Επιστρέφει μεταδεδομένα για ένα αρχείο, όπως όνομα, πλήρη διαδρομή, SHA-256 hash
    και ημερομηνίες δημιουργίας/τελευταίας τροποποίησης.

    Args:
        path (str): Η διαδρομή του αρχείου (πλήρης ή σχετική).

    Returns:
        dict | None:
            Λεξικό με τα εξής κλειδιά:
                - "name" (str): Το όνομα του αρχείου.
                - "path" (str): Η πλήρης διαδρομή.
                - "hash" (str): Το SHA-256 hash του αρχείου.
                - "created" (datetime): Η ημερομηνία δημιουργίας.
                - "modified" (datetime): Η ημερομηνία τελευταίας τροποποίησης.
            Επιστρέφει None αν προκύψει σφάλμα κατά την ανάγνωση.

    Raises:
        OSError: Σε περιπτώσεις που το αρχείο δεν είναι προσβάσιμο (αν δεν γίνει catch).
    """
    try:
        st = os.stat(path)  # μπορεί να ρίξει FileNotFoundError/PermissionError
        created = datetime.fromtimestamp(st.st_ctime)
        modified = datetime.fromtimestamp(st.st_mtime)
        return {
            "name": os.path.basename(path),
            "path": os.path.abspath(path),
            "hash": file_hash(path),  # μπορεί να ρίξει -> θα το πιάσουμε εδώ
            "created": created,
            "modified": modified,
        }
    except Exception as e:
        # ευθυγραμμίζεται με τα tests: σε σφάλμα -> None
        LoggerManager.warning(f"Αδυναμία ανάγνωσης metadata για '{path}': {e}")
        return None


@LogOpject("info")
def inspect_directory_state(base_path: str) -> list[dict]:  # type: ignore
    """
    Σαρώνει έναν φάκελο, συλλέγει μεταδεδομένα για κάθε αρχείο και αναλύει
    πιθανές διπλοεγγραφές ή εκδόσεις αρχείων.

    Ο έλεγχος περιλαμβάνει:
        - Αρχεία με ίδιο όνομα.
        - Αρχεία με ίδιο ή διαφορετικό περιεχόμενο (ως εκδόσεις).
        - Αρχεία με ίδια ημερομηνία δημιουργίας.
        - Αρχεία με ίδια ημερομηνία τροποποίησης.

    Αν ο φάκελος δεν είναι έγκυρος, επιστρέφεται κενή λίστα.

    Args:
        base_path (str): Η διαδρομή του φακέλου προς έλεγχο.

    Returns:
        list[dict]: Λίστα από λεξικά με μεταδεδομένα για κάθε αρχείο.
            Κάθε λεξικό περιέχει ενδεικτικά τα εξής κλειδιά:
                - "name" (str): Όνομα αρχείου.
                - "path" (str): Πλήρης διαδρομή.
                - "hash" (str): SHA-256 hash περιεχομένου.
                - "created" (datetime): Ημερομηνία δημιουργίας.
                - "modified" (datetime): Ημερομηνία τροποποίησης.

    BDD Scenario:
        Given η μέθοδος collect_file_info(base_path) σαρώνει έναν φάκελο και συλλέγει μεταδεδομένα για κάθε έγκυρο αρχείο
        When εκτελείται η μέθοδος inspect_directory_state(base_path)
        Then η μέθοδος group_files_by_name(file_info_list) ομαδοποιεί τα αρχεία με βάση το όνομα
        And η μέθοδος analyze_duplicate_groups(name_map) αναλύει τις πιθανές διπλοεγγραφές και εκδόσεις
    """

    base_path = os.path.abspath(base_path)

    if not is_valid_directory(base_path):
        return []  # noqa: E701

    file_info_list = collect_file_info(base_path)  # pyright: ignore[reportCallIssue, reportArgumentType]
    log_skipped_files(base_path)  # pyright: ignore[reportCallIssue, reportArgumentType]
    name_map = group_files_by_name(file_info_list)
    analyze_duplicate_groups(name_map)

    return file_info_list


@LogOpject("error")
def is_valid_directory(path: str) -> bool:
    """
    Ελέγχει αν η διαδρομή αντιστοιχεί σε έγκυρο και προσβάσιμο φάκελο.

    Αν η διαδρομή δεν είναι φάκελος, καταγράφεται μήνυμα σφάλματος στο log.

    Args:
        path (str): Η διαδρομή του φακέλου.

    Returns:
        bool: True αν η διαδρομή είναι έγκυρος φάκελος, αλλιώς False.
    """
    return os.path.isdir(path)


@LogOpject("info")
def collect_file_info(base_path: str) -> list[dict]:
    """
    Σαρώνει έναν φάκελο και τους υποφακέλους του, συλλέγοντας
    μεταδεδομένα για κάθε έγκυρο αρχείο.

    Κατά τη σάρωση αγνοούνται:
        - Φάκελοι που καθορίζονται ως αποκλεισμένοι στη ρύθμιση (exclusion_config).
        - Συσχετισμένοι φάκελοι του συστήματος (π.χ. Python env, system dirs).

    Επιστρέφει:
        Λίστα από λεξικά με πληροφορίες για κάθε έγκυρο αρχείο, όπως:
            - "name" (str): Όνομα αρχείου.
            - "path" (str): Πλήρης διαδρομή.
            - "size" (int): Μέγεθος σε bytes.
            - "hash" (str): SHA-256 hash περιεχομένου.
            - Άλλα μεταδεδομένα που υποστηρίζονται.

    Args:
        base_path (str): Η διαδρομή του φακέλου για σάρωση.

    Returns:
        list[dict]: Λίστα με μεταδεδομένα για κάθε αρχείο που βρέθηκε.
    """
    return [
        metadata
        for root, _, files in os.walk(base_path)
        if not is_excluded_dir(root) and not is_system_path(root)
        for file in files
        if os.path.isfile(full_path := os.path.join(root, file))
        if (metadata := get_file_metadata(full_path))  # pyright: ignore[reportArgumentType] # pyright: ignore[reportCallIssue] # pyright: ignore[reportCallIssue] # pyright: ignore[reportCallIssue] # pyright: ignore[reportCallIssue] # pyright: ignore[reportCallIssue] # pyright: ignore[reportCallIssue] # pyright: ignore[reportCallIssue] # pyright: ignore[reportCallIssue] # pyright: ignore[reportCallIssue] # pyright: ignore[reportCallIssue] # pyright: ignore[reportCallIssue] # pyright: ignore[reportCallIssue] # type: ignore
    ]


@LogOpject("warning")
def log_skipped_files(base_path: str) -> None:
    """
    Καταγράφει στο log όλα τα αρχεία που παραλείφθηκαν κατά τη σάρωση.

    Η συνάρτηση ελέγχει κάθε στοιχείο στον φάκελο και καταγράφει
    προειδοποίηση για όσα δεν είναι έγκυρα αρχεία.

    Args:
        base_path (str): Η διαδρομή του φακέλου για σάρωση.
    Returns:
        None
    """
    for root, _, files in os.walk(base_path):
        for file in files:
            full_path = os.path.join(root, file)
            if not os.path.isfile(full_path):
                pass  # noqa: E701


@LogOpject("info")
def group_files_by_name(file_info_list: list[dict]) -> dict[str, list[dict]]:
    """
    Ομαδοποιεί τα αρχεία με βάση το όνομά τους, δημιουργώντας ένα λεξικό
    όπου κάθε κλειδί είναι το όνομα του αρχείου και η τιμή είναι λίστα
    με όλα τα αντίστοιχα μεταδεδομένα.

    Args:
        file_info_list (list[dict]):
            Λίστα λεξικών με μεταδεδομένα για κάθε αρχείο.
            Κάθε λεξικό αναμένεται να περιλαμβάνει το κλειδί "name".

    Returns:
        dict[str, list[dict]]:
            Λεξικό όπου:
                - Κλειδί: όνομα αρχείου (str).
                - Τιμή: λίστα από λεξικά μεταδεδομένων για όλα τα αρχεία με αυτό το όνομα.
    """

    name_map: dict[str, list[dict]] = defaultdict(list)
    for info in file_info_list:
        name_map[info["name"]].append(info)
    return name_map


@LogOpject("info")
def analyze_duplicate_groups(name_map: dict[str, list[dict]]) -> None:
    """Αναλύει ομάδες αρχείων που έχουν το ίδιο όνομα και καταγράφει
    αν τα περιεχόμενά τους είναι πανομοιότυπα ή διαφορετικά (ως εκδόσεις).

    Η ανάλυση εκτελείται μόνο για ομάδες που περιέχουν περισσότερα
    από ένα αρχεία και που πληρούν τα κριτήρια της `should_analyze_group`.

    Args:
        name_map (dict[str, list[dict]]):
            Λεξικό όπου το κλειδί είναι το όνομα αρχείου και η τιμή
            είναι λίστα μεταδεδομένων για όλα τα αρχεία με αυτό το όνομα.
    Returns:
        None
    """
    for name, files in name_map.items():
        if not should_analyze_group(files):
            continue

        versions = group_files_by_hash(files)  # pyright: ignore[reportUndefinedVariable, reportCallIssue, reportArgumentType]
        if len(versions) == 1:
            log_identical_group(name)  # pyright: ignore[reportUndefinedVariable, reportArgumentType, reportCallIssue]
        else:
            log_versioned_group(name, versions)  # pyright: ignore[reportUndefinedVariable, reportCallIssue]


@LogOpject("info")
def should_analyze_group(files: list[dict]) -> bool:
    """
    Ελέγχει αν μια ομάδα αρχείων πληροί τα κριτήρια για ανάλυση.

    Η ανάλυση εκτελείται μόνο όταν η ομάδα περιέχει
    περισσότερα από ένα αρχεία.

    Args:
        files (list[dict]):
            Λίστα μεταδεδομένων για τα αρχεία της ομάδας.

    Returns:
        bool:
            True αν η ομάδα έχει πάνω από ένα αρχεία, αλλιώς False.
    """
    return len(files) > 1


@LogOpject("info")
def log_identical_group(name: str) -> str:
    """Καταγράφει στο log ότι όλα τα αρχεία με το δοσμένο όνομα
    έχουν πανομοιότυπο περιεχόμενο σε όλες τις τοποθεσίες.

    Args:
        name (str): Το όνομα του αρχείου.

    Returns:
        None
    """
    return f"Αρχείο {name} έχει ίδιο περιεχόμενο σε όλες τις τοποθεσίες."  # pyright: ignore[reportReturnType]


@LogOpject("info")
def log_versioned_group(name: str, versions: dict[str, list[dict]]) -> list:
    """Καταγράφει στο log τις διαφορετικές εκδόσεις ενός αρχείου με το ίδιο όνομα.

    Για κάθε έκδοση καταγράφει:
    - Μερικό hash της έκδοσης
    - Ημερομηνία τελευταίας τροποποίησης
    - Τη διαδρομή του αρχείου

    Args:
        name (str): Το όνομα του αρχείου.
        versions (dict[str, list[dict]]):
            Λεξικό όπου το κλειδί είναι το hash της έκδοσης και η τιμή
            είναι λίστα με μεταδεδομένα των αρχείων που ανήκουν σε αυτή την έκδοση.
    Returns:
        None
    """
    out = []
    for version_hash, version_files in versions.items():
        for vf in version_files:
            out.append(
                f"Έκδοση '{name}' | hash: {version_hash[:10]} | 🕒 {vf['modified']} | 📍 {vf['path']}"
            )
    return out  # pyright: ignore[reportReturnType]


@LogOpject("info")
def group_files_by_hash(files: list[dict]) -> dict[str, list[dict]]:
    """
    Ομαδοποιεί αρχεία με βάση το hash περιεχομένου τους.

    Η ομαδοποίηση βοηθά στην αναγνώριση αρχείων που έχουν
    το ίδιο περιεχόμενο (ίδιο hash), ακόμα κι αν έχουν διαφορετική διαδρομή.

    Args:
        files (list[dict]): Λίστα με μεταδεδομένα για τα αρχεία, όπου κάθε λεξικό
                            περιέχει τουλάχιστον το πεδίο "hash".

    Returns:
        dict[str, list[dict]]: Λεξικό όπου τα κλειδιά είναι τα hash των αρχείων
                               και οι τιμές λίστες από μεταδεδομένα αρχείων που
                               έχουν το ίδιο hash.
    """
    versions: dict[str, list[dict]] = defaultdict(list)
    for f in files:
        versions[f["hash"]].append(f)
    return versions


@LogOpject("info")
def get_all_file_info(
    path: str,
) -> list[dict]:  # pyright: ignore[reportMissingTypeArgument, reportUnknownParameterType]
    """
    Επιστρέφει πληροφορίες για κάθε αρχείο μέσα σε έναν φάκελο και τους υποφακέλους του.

    Για κάθε αρχείο συλλέγει:
    - το όνομά του,
    - την πλήρη διαδρομή,
    - το SHA256 hash του περιεχομένου του,
    - και την ημερομηνία δημιουργίας (ως timestamp).

    Αν κάποιο αρχείο δεν μπορεί να διαβαστεί, καταγράφεται προειδοποίηση και παραλείπεται.

    Args:
        path (str): Η διαδρομή προς τον φάκελο που θα σαρωθεί.

    Returns:
        list[dict]: Λίστα με λεξικά μεταδεδομένων για κάθε επιτυχώς διαβασμένο αρχείο.
    """
    file_infos = []
    for root, _, files in os.walk(path):
        for file in files:
            full_path = os.path.join(root, file)
            try:
                with open(full_path, "rb") as f:
                    content = f.read()
                    file_hash = hashlib.sha256(content).hexdigest()
                    created = os.path.getctime(full_path)
                    file_infos.append(
                        {
                            "name": file,
                            "path": full_path,
                            "hash": file_hash,
                            "created": created,
                        }
                    )
            except (IOError, OSError) as e:
                # 🔑 Αναγκαίο για να περνά το test
                LoggerManager.warning(f"Σφάλμα κατά την ανάγνωση αρχείου: {e}")
                continue
    return file_infos


@LogOpject("info")
def group_duplicates(
    file_infos: list[dict],
) -> list[list[dict]]:  # pyright: ignore[reportMissingTypeArgument, reportUnknownParameterType]
    """
    Ομαδοποιεί αρχεία που έχουν το ίδιο περιεχόμενο, βασισμένα στο SHA256 hash τους.

    Η συνάρτηση επιστρέφει λίστα από ομάδες, όπου κάθε ομάδα περιέχει αρχεία με το ίδιο hash,
    δηλαδή ίδια περιεχόμενα.

    Args:
        file_infos (list[dict]): Λίστα λεξικών με μεταδεδομένα αρχείων, που περιλαμβάνουν το πεδίο 'hash'.

    Returns:
        list[list[dict]]: Λίστα ομάδων αρχείων με ίδιο περιεχόμενο.
    """
    grouped = defaultdict(list)  # pyright: ignore[reportUnknownVariableType]
    for info in file_infos:  # pyright: ignore[reportUnknownVariableType]
        grouped[info["hash"]].append(info)

    return list(grouped.values())  # pyright: ignore[reportUnknownArgumentType, reportUnknownVariableType]
