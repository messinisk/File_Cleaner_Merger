"""
exclusion_config.py
Αυτό το αρχείο περιέχει ρυθμίσεις για την εξαίρεση φακέλων και διαδρομών
από την επεξεργασία σε ένα πρόγραμμα Python. Περιλαμβάνει λίστες φακέλων
που πρέπει να αγνοούνται και συνθήκες για τον εντοπισμό συστημικών διαδρομών
ανάλογα με το λειτουργικό σύστημα.
"""

# exclusion_config.py
import os
import platform
import re

# Λίστα φακέλων που θα εξαιρούνται από την επεξεργασία

CURRENT_OS = platform.system()


def is_excluded_dir(path: str) -> bool:
    """
    Ελέγχει αν μια διαδρομή (path) περιέχει φάκελο που ταιριάζει σε προκαθορισμένο μοτίβο αποκλεισμένων φακέλων.

    Η συνάρτηση χρησιμοποιεί κανονική έκφραση (regex) για να ελέγξει αν κάποιο τμήμα της διαδρομής
    αντιστοιχεί σε γνωστά ονόματα φακέλων που πρέπει να αγνοούνται (π.χ. αρχεία cache, ρυθμίσεων ή περιβάλλοντος).

    Args:
        path (str): Απόλυτη ή σχετική διαδρομή που θα ελεγχθεί.

    Returns:
        bool:
            - `True` αν η διαδρομή περιέχει αποκλεισμένο φάκελο.
            - `False` αν δεν περιέχει κανέναν αποκλεισμένο φάκελο.

    Παράδειγμα:
        >>> is_excluded_dir("project/.git/config")
        True
        >>> is_excluded_dir("project/src/module")
        False
    """
    pattern = r"(?:__pycache__|__init__\.py|\.git|\.vscode|\.ruff_cache|\.pytest_cache|htmlcov|venv|env|\.mypy_cache|\.idea|node_modules)"
    path_parts = os.path.normpath(path).split(os.sep)
    return any(re.fullmatch(pattern, part) for part in path_parts)


def is_system_path(path: str) -> bool:
    """
    Ελέγχει αν μια διαδρομή (path) ανήκει σε system-level τοποθεσία, ανάλογα με το λειτουργικό σύστημα.

    Η συνάρτηση συγκρίνει την απόλυτη διαδρομή με προκαθορισμένα μοτίβα (regex patterns)
    που αντιστοιχούν σε συστημικούς φακέλους για το τρέχον λειτουργικό σύστημα (`CURRENT_OS`).

    Parameters
    ----------
    path : str
        Η απόλυτη ή σχετική διαδρομή που θα ελεγχθεί.

    Returns
    -------
    bool
        - `True` αν η διαδρομή ξεκινάει από system-level τοποθεσία.
        - `False` διαφορετικά.

    Notes
    -----
    - Τα regex patterns είναι ορισμένα σε λεξικό με κλειδιά τα ονόματα λειτουργικών συστημάτων
      και τιμές τα αντίστοιχα κανονικά εκφράσματα που περιγράφουν τις system-level τοποθεσίες.
    - Το `CURRENT_OS` είναι string που περιγράφει το λειτουργικό σύστημα (π.χ. `"Windows"`, `"Linux"`, `"Darwin"`).

    Examples
    --------
    >>> CURRENT_OS = "Linux"
    >>> is_system_path("/etc/passwd")
    True
    >>> is_system_path("/home/user/file.txt")
    False
    """
    abs_path = os.path.abspath(path)

    # Ορισμός regex pattern ανά OS
    patterns = {
        "Windows": r"^(?:[A-Za-z]:\\Windows|[A-Za-z]:\\Program Files|[A-Za-z]:\\ProgramData)(?:\\|$)",
        "Linux": r"^(?:/proc|/dev|/sys|/run|/boot)(?:/|$)",
        "Darwin": r"^(?:/System|/private|/Volumes)(?:/|$)",
        "Android": r"^(?:/proc|/dev|/system|/vendor)(?:/|$)",
    }

    pattern = patterns.get(CURRENT_OS)
    return bool(pattern and re.match(pattern, abs_path))
