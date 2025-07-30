import os
import platform


# Ονόματα φακέλων που θέλουμε πάντα να αγνοούμε
EXCLUDED_DIR_NAMES = {
    "__pycache__",
    ".git",
    ".vscode",
    ".ruff_cache",
    ".pytest_cache",
    "htmlcov",
    "venv",
    "env",
    ".mypy_cache",
    ".idea",
    "node_modules",
}

# Ριζικά συστήματα που δεν θέλουμε να περνάμε (ανά OS)
SYSTEM_PATH_PREFIXES = {
    "Windows": ["C:\\Windows", "C:\\Program Files", "C:\\ProgramData"],
    "Linux": ["/proc", "/dev", "/sys", "/run", "/boot"],
    "Darwin": ["/System", "/private", "/Volumes"],  # macOS
    "Android": ["/proc", "/dev", "/system", "/vendor"],
}

CURRENT_OS = platform.system()

def is_excluded_dir(path: str) -> bool:
    """Επιστρέφει True αν το path περιέχει κάποιον από τους αποκλεισμένους φακέλους."""
    path_parts = os.path.normpath(path).split(os.sep)
    return any(part in EXCLUDED_DIR_NAMES for part in path_parts)


def is_system_path(path: str) -> bool:
    """Επιστρέφει True αν το path ξεκινάει από system-level διαδρομή ανά OS."""
    abs_path = os.path.abspath(path)
    prefixes = SYSTEM_PATH_PREFIXES.get(CURRENT_OS, [])
    return any(abs_path.startswith(os.path.abspath(p)) for p in prefixes)
