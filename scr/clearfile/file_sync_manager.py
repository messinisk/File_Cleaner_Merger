import logging
import os
import random



logging.basicConfig(
    filename="file_inspector.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

def merge_by_version_date(file_a: dict, file_b: dict) -> None:  # type: ignore
    try:
        created_a = os.path.getctime(file_a["path"])  # type: ignore
        created_b = os.path.getctime(file_b["path"])  # type: ignore

        if created_a <= created_b:
            base = file_a  # type: ignore
            other = file_b  # type: ignore
        else:
            base = file_b  # type: ignore
            other = file_a  # type: ignore

        # Διαβάζουμε το περιεχόμενο του νεότερου αρχείου
        with open(other["path"], "r", encoding="utf-8") as f_other:  # type: ignore
            content_to_merge = f_other.read()

        # Προσθέτουμε στο ΤΕΛΟΣ του παλιού αρχείου
        with open(base["path"], "a", encoding="utf-8") as f_base:  # type: ignore
            f_base.write("\n\n# --- Merged version ---\n")
            f_base.write(f"# Συγχώνευση από: {os.path.basename(other['path'])}\n")  # type: ignore
            f_base.write(content_to_merge)

        # Διαγράφουμε ΜΟΝΟ το άλλο αρχείο
        os.remove(other["path"])  # type: ignore

        logging.info(f"Συγχωνεύθηκαν εκδόσεις: {other['path']} -> {base['path']}")

    except Exception as e:
        logging.error(f"Σφάλμα συγχώνευσης εκδόσεων: {e}")


def merge_random_conflict(file_a: dict, file_b: dict) -> None:  # type: ignore
    chosen, discarded = (
        (file_a, file_b) if random.choice([True, False]) else (file_b, file_a)
    )  # type: ignore

    try:
        with open(discarded["path"], "r", encoding="utf-8") as f_disc:  # type: ignore
            content_to_merge = f_disc.read()

        with open(chosen["path"], "a", encoding="utf-8") as f_chosen:  # type: ignore
            f_chosen.write("\n\n# --- Merged random conflict ---\n")
            f_chosen.write(f"# Συγχώνευση από: {os.path.basename(discarded['path'])}\n")  # type: ignore
            f_chosen.write(content_to_merge)

        os.remove(discarded["path"])  # type: ignore
        logging.info(f"Τυχαία συγχώνευση: {discarded['path']} -> {chosen['path']}")

    except Exception as e:
        logging.error(f"Σφάλμα τυχαίας συγχώνευσης: {e}")

def delete_duplicates(duplicate_files: list[dict]) -> None:  # type: ignore
    duplicate_files[0]  # type: ignore
    for dup in duplicate_files[1:]:  # type: ignore
        try:
            os.remove(dup["path"])  # type: ignore
            logging.info(f"Διαγράφηκε διπλό αρχείο: {dup['path']}")
        except Exception as e:
            logging.error(f"Σφάλμα διαγραφής διπλού: {dup['path']} -> {e}")
