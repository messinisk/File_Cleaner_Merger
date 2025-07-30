 🛠️ File Sync & Clean Tool (Developer Docs)

Το έργο αυτό προσφέρει ένα σύστημα εντοπισμού, σύγκρισης και συγχώνευσης αρχείων με έμφαση στη διατήρηση δεδομένων.

---

## 📁 Δομή Project

# 🧠 Duplicate Detector - Τεκμηρίωση για Προγραμματιστές

Αυτό το έργο εντοπίζει διπλότυπα αρχεία σε ένα φάκελο και καταγράφει τις εκδόσεις τους με βάση το όνομα και το hash (SHA256) του περιεχομένου.

## 📁 Δομή Αρχείων

```
project_root/
├── duplicate_detector.py        # Κύριο αρχείο εντοπισμού διπλότυπων
├── exclusion_config.py         # Ορισμοί εξαιρούμενων paths & συστημάτων
├── exclusion_config.py         # δείριση διαχείρισης/συγχώνευσης διπλότυπων
├── tests/
│   └── test_duplicate_detector.py  # Μονάδες δοκιμών με unittest
|   └──  test_file_sync_manager.py # Μονάδες δοκιμών με unittest
└── file_inspector.log          # Log αρχείο με καταγραφές
```

---

## 🔧 `duplicate_detector.py`

### `inspect_directory_state(base_path: str) -> list[dict]`

Κύρια είσοδος του προγράμματος. Σαρώνει έναν φάκελο και επιστρέφει metadata αρχείων.

### `is_valid_directory(path: str) -> bool`

Επιστρέφει True αν το path είναι έγκυρος φάκελος, αλλιώς False και κάνει log.

### `collect_file_info(base_path: str) -> list[dict]`

Σαρώνει φακέλους και συλλέγει metadata για κάθε αρχείο, **παραλείποντας εξαιρούμενα ή system paths**.

### `log_skipped_files(base_path: str)`

Καταγράφει αρχεία που δεν είναι κανονικά (π.χ. symlinks, broken paths).

### `group_files_by_name(file_info_list: list[dict]) -> dict[str, list[dict]]`

Ομαδοποιεί τα αρχεία κατά όνομα (basename).

### `analyze_duplicate_groups(name_map: dict[str, list[dict]])`

Για κάθε όνομα με πολλαπλά αρχεία, εντοπίζει εκδόσεις βάσει hash και καταγράφει τιμές στο log.

### `should_analyze_group(files: list[dict]) -> bool`

True αν υπάρχουν >1 αρχεία με το ίδιο όνομα.

### `log_identical_group(name: str)`

Καταγράφει ότι όλες οι εκδόσεις έχουν ίδιο περιεχόμενο.

### `log_versioned_group(name: str, versions: dict[str, list[dict]])`

Καταγράφει αναλυτικά κάθε έκδοση του αρχείου (hash, τροποποίηση, διαδρομή).

### `group_files_by_hash(files: list[dict]) -> dict[str, list[dict]]`

Ομαδοποιεί τα αρχεία με βάση το hash περιεχομένου.

### `get_file_metadata(path: str) -> dict | None`

Επιστρέφει μεταδεδομένα για ένα αρχείο: όνομα, path, hash, created/modified.

### `file_hash(path: str) -> str`

Υπολογίζει SHA256 hash του αρχείου.

### `get_all_file_info(path: str) -> list[dict]`

Εναλλακτική μαζική ανάγνωση αρχείων με περιεχόμενο + hash.

### `group_duplicates(file_infos: list[dict]) -> list[list[dict]]`

Επιστρέφει λίστα από λίστες με διπλότυπα αρχεία (ίδιο hash).

---

## 🔒 `exclusion_config.py`

### `EXCLUDED_DIR_NAMES`

Σετ από ονόματα φακέλων που αγνοούνται (π.χ. `__pycache__`, `.vscode`).

### `SYSTEM_PATH_PREFIXES`

Διαδρομές ανά OS που χαρακτηρίζονται ως "σύστημα" (π.χ. `C:\Windows`, `/proc`).

### `is_excluded_dir(path: str) -> bool`

Επιστρέφει True αν κάποιος φάκελος στο path είναι στην EXCLUDED λίστα.

### `is_system_path(path: str) -> bool`

Επιστρέφει True αν το path ξεκινά από προκαθορισμένο system path.

# 🧠 Duplicate Detector - Τεκμηρίωση για Προγραμματιστές

Αυτό το έργο εντοπίζει διπλότυπα αρχεία σε ένα φάκελο και καταγράφει τις εκδόσεις τους με βάση το όνομα και το hash (SHA256) του περιεχομένου.



## 🔧 `file_sync_manager.py`

### `merge_by_version_date(file_a: dict, file_b: dict) -> None`

Συγχωνεύει δύο εκδόσεις αρχείων κρατώντας το παλαιότερο ως βάση.

* Αντιγράφει το περιεχόμενο του νεότερου στο τέλος του παλαιότερου.
* Καταγράφει την ενέργεια στο log.
* Διαγράφει το νεότερο αρχείο.

### `merge_random_conflict(file_a: dict, file_b: dict) -> None`

Επιλύει διπλότυπο με τυχαία επιλογή αρχείου:

* Το περιεχόμενο του "χαμένου" συγχωνεύεται στο τέλος του "νικητή".
* Το "χαμένο" αρχείο διαγράφεται.
* Καταγράφει τις ενέργειες στο log.

### `delete_duplicates(duplicate_files: list[dict]) -> None`

Διαγράφει όλα τα αρχεία της λίστας `duplicate_files` εκτός του πρώτου.

* Καταγράφει τη διαγραφή στο log.
* Παραλείπει το πρώτο ως κύρια έκδοση.


---

## 🧪 `tests/test_duplicate_detector.py`

Unit tests με χρήση `unittest` και `tempfile`. Ελέγχονται:

* Ανίχνευση διπλότυπων αρχείων
* Δημιουργία αρχείου log
* Edge cases:

  * Άδειος φάκελος
  * Μη έγκυρη διαδρομή
  * Εξαιρούμενοι φάκελοι (`__pycache__`)
  * `is_system_path()` σε Windows


## 🧪 tests/test_file_sync_manager.py

TestFileSyncManager

Κλάση unit tests για τις συναρτήσεις του merge_utils.py.

### setUp() / tearDown()

* Δημιουργία και καθαρισμός προσωρινού φακέλου με tempfile.mkdtemp() και shutil.rmtree()._create_file(name, content, created_time=None)

* Βοηθητική συνάρτηση για τη δημιουργία αρχείων σε tests με δυνατότητα ορισμού ημερομηνίας δημιουργίας (created_time).

### test_merge_by_version_date()

* Δημιουργεί δύο αρχεία με διαφορετικό created_time.

* Ελέγχει ότι το περιεχόμενο του νεότερου συγχωνεύεται στο τέλος του παλαιότερου.Ελέγχει ότι το νεότερο διαγράφεται.

### est_merge_random_conflict()

* Δημιουργεί δύο διπλότυπα αρχεία. 
Ελέγχει ότι το ένα διατηρείται και το περιεχόμενο του άλλου συγχωνεύεται.

### test_delete_duplicates()

* Δημιουργεί δύο αρχεία με ίδιο περιεχόμενο. 
Ελέγχει ότι μόνο ένα παραμένει μετά τη διαγραφή.
---

## 📓 Σημειώσεις για Ανάπτυξη

* Υποστηρίζονται: **Windows / Linux / macOS / Android**
* Logging σε αρχείο `file_inspector.log`
* Δεν χρησιμοποιείται `print()` για UI – έτοιμο για GUI/CLI ενσωμάτωση
* Κώδικας πλήρως συμβατός με `ruff`, `mypy`, `pyright`, `radon`

---

## ✅ Παραδείγματα χρήσης

```python
from duplicate_detector import inspect_directory_state

results = inspect_directory_state("/path/to/scan")
for f in results:
    print(f["name"], f["hash"])
```

---

## 📬 Συνεισφορά

Αν θες να συνεισφέρεις:

* Δες πρώτα τον φάκελο `tests/`
* Υπέβαλε Pull Request με νέα tests ή λειτουργίες
* Τήρησε τις δομές `radon A`, `type hints`, `logging`

---

Καλή χρήση! 🚀
