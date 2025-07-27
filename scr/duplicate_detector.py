# Εστιάζει στον εντοπισμό διπλότυπων
import hashlib
import logging
import os
from collections import defaultdict
from datetime import datetime

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


# -------------------------------
# 📄 Ανάκτηση μεταδεδομένων αρχείου
# -------------------------------
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
        logging.error(f"Σφάλμα κατά την ανάγνωση του αρχείου: {path} -> {e}")
        return None


# -------------------------------
# 🧩 Κύρια συνάρτηση σάρωσης φακέλου
# -------------------------------
def inspect_directory_state(base_path: str) -> list[dict]:  # type: ignore
    """
    Σαρώνει φάκελο και εντοπίζει αρχεία με:
    - ίδιο όνομα
    - ίδιο ή διαφορετικό περιεχόμενο (ως εκδόσεις)
    - ίδια ημερομηνία δημιουργίας
    """
    file_info_list = []
    base_path = os.path.abspath(base_path)
    if not os.path.isdir(base_path):
        logging.error(f"Η διαδρομή δεν είναι έγκυρος φάκελος: {base_path}")
        return []

    for root, _, files in os.walk(base_path):
        for file in files:
            full_path = os.path.join(root, file)
            if os.path.isfile(full_path):
                metadata = get_file_metadata(full_path)  # type: ignore
                if metadata:
                    file_info_list.append(metadata)  # type: ignore
            else:
                logging.warning(f"Παραλείφθηκε (δεν είναι αρχείο): {full_path}")

    # Ομαδοποίηση κατά όνομα αρχείου
    name_map = defaultdict(list)  # type: ignore
    for info in file_info_list:  # type: ignore
        name_map[info["name"]].append(info)  # type: ignore

    print(f"\n📂 Σάρωση φακέλου: {base_path}\n")

    for name, files in name_map.items():  # type: ignore
        if len(files) == 1:  # type: ignore
            continue

        # Ομαδοποίηση κατά περιεχόμενο (hash)
        versions: dict[str, list[dict]] = defaultdict(list)

        for f in files:  # type: ignore
            versions[f["hash"]].append(f)  # type: ignore

        print(f"📄 Αρχείο με ίδιο όνομα: {name}")

        if len(versions) == 1:  # type: ignore
            print("  ✅ Ίδιο περιεχόμενο σε όλες τις τοποθεσίες")
        else:
            print("  🌀 Διαφορετικές εκδόσεις:")
            for version_hash, version_files in versions.items():  # type: ignore
                print(f"    🔸 Έκδοση (hash: {version_hash[:10]}...)")
                for vf in version_files:
                    print(f" → {vf['path']} | 🕒 {vf['modified']}")
                    logging.info(f"Έκδοση αρχείου '{name}' σε {vf['path']}")

    return file_info_list


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
            except Exception as e:  # pyright: ignore[reportUnusedVariable]  # noqa: F841
                continue  # Αν κάποιο αρχείο δεν μπορεί να διαβαστεί, απλώς το παραλείπουμε
    return file_infos  # pyright: ignore[reportUnknownVariableType]


def group_duplicates(
    file_infos: list[dict],
) -> list[list[dict]]:  # pyright: ignore[reportMissingTypeArgument, reportUnknownParameterType]
    """Ομαδοποιεί αρχεία με βάση το hash."""
    grouped = defaultdict(list)  # pyright: ignore[reportUnknownVariableType]
    for info in file_infos:  # pyright: ignore[reportUnknownVariableType]
        grouped[info["hash"]].append(info)  # pyright: ignore[reportUnknownMemberType]

    return list(grouped.values())  # pyright: ignore[reportUnknownArgumentType, reportUnknownVariableType]


if __name__ == "__main__":
    print(inspect_directory_state("./"))  # type: ignore
