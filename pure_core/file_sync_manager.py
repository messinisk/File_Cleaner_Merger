"""
Συγχωνεύει δύο αρχεία με βάση την ημερομηνία και ώρα δημιουργίας ή με τυχαία επιλογή.
Επίσης, παρέχει δυνατότητα διαγραφής διπλών αρχείων.
"""

import os
import secrets
from typing import Dict
from pure_core.logfile import LogOpject


@LogOpject("info")
def merge_by_version_date(file_a: Dict, file_b: Dict) -> str:
    """Συγχωνεύει δύο αρχεία με βάση την ημερομηνία δημιουργίας τους."""

    created_a = os.path.getctime(file_a["path"])
    created_b = os.path.getctime(file_b["path"])

    # Επιλογή με βάση ποιο αρχείο είναι παλιότερο
    base, other = (file_a, file_b) if created_a <= created_b else (file_b, file_a)

    # Αν τα timestamps είναι ίδια, διαλέγουμε file_a ως base
    if created_a == created_b:
        base, other = file_a, file_b

    # Διαβάζουμε το περιεχόμενο του νεότερου αρχείου
    with open(other["path"], "r", encoding="utf-8") as f_other:
        content_to_merge = f_other.read()

    # Προσθέτουμε στο τέλος του παλιού αρχείου
    with open(base["path"], "a", encoding="utf-8") as f_base:
        f_base.write("\n\n# --- Merged version ---\n")
        f_base.write(f"# Συγχώνευση από: {os.path.basename(other['path'])}\n")
        f_base.write(content_to_merge)

    # Διαγράφουμε το άλλο αρχείο
    os.remove(other["path"])

    return f"Συγχωνεύθηκαν εκδόσεις: {other['path']} -> {base['path']}"


@LogOpject("info")
def merge_random_conflict(file_a: dict, file_b: dict) -> str:  # type: ignore
    """Συγχωνεύει δύο αρχεία τυχαία."""

    chosen, discarded = (
        (file_a, file_b) if secrets.choice([True, False]) else (file_b, file_a)
    )  # type: ignore

    with open(discarded["path"], "r", encoding="utf-8") as f_disc:  # type: ignore
        content_to_merge = f_disc.read()

    with open(chosen["path"], "a", encoding="utf-8") as f_chosen:  # type: ignore
        f_chosen.write("\n\n# --- Merged random conflict ---\n")
        f_chosen.write(f"# Συγχώνευση από: {os.path.basename(discarded['path'])}\n")  # type: ignore
        f_chosen.write(content_to_merge)

    os.remove(discarded["path"])  # type: ignore
    return f"Τυχαία συγχώνευση: {discarded['path']} -> {chosen['path']}"  # pyright: ignore[reportReturnType]


@LogOpject("info")
def delete_duplicates(duplicate_files: list[dict]) -> str:  # type: ignore
    """Διαγράφει τα διπλά αρχεία, κρατώντας το πρώτο."""

    for dup in duplicate_files[1:]:  # type: ignore
        os.remove(dup["path"])  # type: ignore
    return f"Διαγράφηκαν {len(duplicate_files) - 1} διπλά"  # pyright: ignore[reportReturnType]
