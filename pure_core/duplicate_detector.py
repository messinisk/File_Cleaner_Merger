"""
duplicate detection : ανίχνευση διπλοτύπων
Εστιάζει στον εντοπισμό διπλότυπων αρχείων σε έναν φάκελο. :
It focuses on identifying duplicate files in a folder.
    Returns:
        _type_: _description_
"""

import hashlib
import logging
import os
from asyncio.log import logger
from collections import defaultdict
from datetime import datetime

from pure_core.exclusion_config import is_excluded_dir, is_system_path

# -------------------------------
# 🔧 Ρύθμιση του logging
# -------------------------------
logging.basicConfig(
    filename="file_inspector.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


# -------------------------------
# 🔍 Υπολογισμός hash αρχείου
# -------------------------------


def file_hash(path):  # type: ignore
    """Υπολογίζει SHA256 hash του αρχείου."""
    hasher = hashlib.sha256()
    with open(path, "rb") as f:  # type: ignore
        while chunk := f.read(8192):
            hasher.update(chunk)
    return hasher.hexdigest()


def get_file_metadata(path):  # type: ignore
    """Επιστρέφει όνομα, διαδρομή, hash, ημερομηνία δημιουργίας/τροποποίησης."""
    try:
        stat = os.stat(path)  # type: ignore
        return {
            "name": os.path.basename(path),  # type: ignore
            "path": path,
            "hash": file_hash(path),  # type: ignore
            "created": datetime.fromtimestamp(stat.st_ctime),
            "modified": datetime.fromtimestamp(stat.st_mtime),
        }
    except Exception as e:
        logging.warning(
            f"Σφάλμα κατά\
            την ανάγνωση του αρχείου: {path} -> {e}"
        )
        return None


def inspect_directory_state(base_path: str) -> list[dict]:  # type: ignore
    """
    Σαρώνει φάκελο και εντοπίζει αρχεία με:
    - ίδιο όνομα
    - ίδιο ή διαφορετικό περιεχόμενο (ως εκδόσεις)
    - ίδια ημερομηνία δημιουργίας
    """
    base_path = os.path.abspath(base_path)

    if not is_valid_directory(base_path):  # pyright: ignore[reportCallIssue, reportArgumentType]
        return []

    file_info_list = collect_file_info(base_path)  # pyright: ignore[reportCallIssue, reportArgumentType]
    log_skipped_files(base_path)  # pyright: ignore[reportCallIssue, reportArgumentType]
    name_map = group_files_by_name(file_info_list)
    analyze_duplicate_groups(name_map)

    return file_info_list


def is_valid_directory(path: str) -> bool:
    """Επιστρέφει True αν η διαδρομή είναι\
    έγκυρος φάκελος, αλλιώς κάνει log και False."""
    if not os.path.isdir(path):
        logging.error(f"Η διαδρομή δεν είναι έγκυρος φάκελος: {path}")
        return False
    return True


def collect_file_info(base_path: str) -> list[dict]:
    """
    Επιστρέφει λίστα μεταδεδομένων για κάθε αρχείο\
    μέσα σε έναν φάκελο και τους υποφακέλους του.

    Αγνοεί:
    - Φακέλους που καθορίζονται ως αποκλεισμένοι\
    από τη ρύθμιση (exclusion_config)
    - Συσχετισμένους φακέλους του συστήματος\
    (όπως Python env, system dirs)

    Επιστρέφει:
    - Λίστα από λεξικά με πληροφορίες για κάθε έγκυρο αρχείο\
    (π.χ. όνομα, διαδρομή, μέγεθος, hash κ.ά.)
    """
    return [
        metadata
        for root, _, files in os.walk(base_path)
        if not is_excluded_dir(root) and not is_system_path(root)
        for file in files
        if os.path.isfile(full_path := os.path.join(root, file))
        if (metadata := get_file_metadata(full_path))  # pyright: ignore[reportArgumentType] # pyright: ignore[reportCallIssue] # pyright: ignore[reportCallIssue] # pyright: ignore[reportCallIssue] # pyright: ignore[reportCallIssue] # pyright: ignore[reportCallIssue] # pyright: ignore[reportCallIssue] # pyright: ignore[reportCallIssue] # pyright: ignore[reportCallIssue] # pyright: ignore[reportCallIssue] # pyright: ignore[reportCallIssue] # pyright: ignore[reportCallIssue] # pyright: ignore[reportCallIssue] # type: ignore
    ]


def log_skipped_files(base_path: str) -> None:
    """Κάνει logging για κάθε στοιχείο που δεν είναι αρχείο."""
    for root, _, files in os.walk(base_path):
        for file in files:
            full_path = os.path.join(root, file)
            if not os.path.isfile(full_path):
                logging.warning(f"Παραλείφθηκε (δεν είναι αρχείο): {full_path}")


def group_files_by_name(file_info_list: list[dict]) -> dict[str, list[dict]]:
    """Ομαδοποιεί τα αρχεία με βάση το όνομά τους."""
    name_map: dict[str, list[dict]] = defaultdict(list)
    for info in file_info_list:
        name_map[info["name"]].append(info)
    return name_map


def analyze_duplicate_groups(name_map: dict[str, list[dict]]) -> None:
    """Αναλύει τα αρχεία με ίδιο όνομα και καταγράφει αν είναι ίδια ή διαφορετικά."""
    for name, files in name_map.items():
        if not should_analyze_group(files):
            continue

        versions = group_files_by_hash(files)  # pyright: ignore[reportCallIssue, reportArgumentType]
        if len(versions) == 1:
            log_identical_group(name)  # pyright: ignore[reportArgumentType, reportCallIssue]
        else:
            log_versioned_group(name, versions)  # pyright: ignore[reportCallIssue]


def should_analyze_group(files: list[dict]) -> bool:
    """Επιστρέφει True αν η λίστα έχει περισσότερα από 1 αρχεία."""
    return len(files) > 1


def log_identical_group(name: str) -> None:
    """Καταγράφει ότι όλα τα αρχεία είναι ίδια."""
    logger.info(f"Αρχείο '{name}' έχει ίδιο περιεχόμενο σε όλες τις τοποθεσίες.")


def log_versioned_group(name: str, versions: dict[str, list[dict]]) -> None:
    """Καταγράφει τις διαφορετικές εκδόσεις του αρχείου."""
    logger.info(f"Αρχείο '{name}' έχει διαφορετικές εκδόσεις:")
    for version_hash, version_files in versions.items():
        for vf in version_files:
            logger.info(
                f"Έκδοση '{name}' | hash: {version_hash[:10]} | 🕒 {vf['modified']} | 📍 {vf['path']}"
            )


def group_files_by_hash(files: list[dict]) -> dict[str, list[dict]]:
    """Ομαδοποιεί αρχεία με βάση το hash."""
    versions: dict[str, list[dict]] = defaultdict(list)
    for f in files:
        versions[f["hash"]].append(f)
    return versions


def get_all_file_info(
    path: str,
) -> list[dict]:  # pyright: ignore[reportMissingTypeArgument, reportUnknownParameterType]
    """Επιστρέφει πληροφορίες για κάθε αρχείο σε μια διαδρομή."""
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
                        {  # pyright: ignore[reportUnknownMemberType]
                            "name": file,
                            "path": full_path,
                            "hash": file_hash,
                            "created": created,
                        }
                    )
            except (IOError, OSError) as e:
                logger.warning("Σφάλμα κατά την ανάγνωση αρχείου: %s", e)
                continue  # Αν κάποιο αρχείο δεν μπορεί να διαβαστεί, απλώς το παραλείπουμε
    return file_infos  # pyright: ignore[reportUnknownVariableType]


def group_duplicates(
    file_infos: list[dict],
) -> list[list[dict]]:  # pyright: ignore[reportMissingTypeArgument, reportUnknownParameterType]
    """Ομαδοποιεί αρχεία με βάση το hash."""
    grouped = defaultdict(list)  # pyright: ignore[reportUnknownVariableType]
    for info in file_infos:  # pyright: ignore[reportUnknownVariableType]
        grouped[info["hash"]].append(info)

    return list(grouped.values())  # pyright: ignore[reportUnknownArgumentType, reportUnknownVariableType]
