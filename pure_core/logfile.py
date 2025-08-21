import logging
from logging import Logger
import sys
from functools import wraps


class LoggerManager:
    """
    Διαχειρίζεται ένα singleton logger για την εφαρμογή.

    Αυτή η κλάση παρέχει κεντρικό σημείο για τη δημιουργία και χρήση ενός logger.
    Όλες οι μέθοδοι είναι κλασικές (classmethods) και λειτουργούν πάνω σε ένα κοινό logger.

    Attributes:
        _logger (Logger | None): Εσωτερική μεταβλητή που κρατά τον logger. Αρχικά None μέχρι την αρχικοποίηση.
    """

    _logger: Logger = logging.getLogger(__name__)

    @classmethod
    def initialize(
        cls, logfile: str = "file_inspector.log", level=logging.INFO
    ) -> None:
        """
        Αρχικοποιεί τον logger αν δεν έχει ήδη δημιουργηθεί.

        Args:
            logfile (str): Το όνομα του αρχείου καταγραφής. Προεπιλογή: "file_inspector.log".
            level (int): Το επίπεδο καταγραφής (logging level). Προεπιλογή: logging.INFO.

        Σημείωση:
            Αν ο logger έχει ήδη αρχικοποιηθεί, η μέθοδος δεν κάνει τίποτα.
        """
        if cls._logger is None:
            logging.basicConfig(
                filename=logfile,
                level=level,
                format="%(asctime)s - %(levelname)s - %(message)s",
            )
            cls._logger = logging.getLogger("FileInspector")

    @classmethod
    def info(cls, message: str) -> None:
        """
        Καταγράφει ένα μήνυμα επιπέδου INFO.

        Args:
            message (str): Το μήνυμα που θα καταγραφεί.
        """
        cls._logger.info(message)

    @classmethod
    def warning(cls, message: str) -> None:
        """
        Καταγράφει ένα μήνυμα επιπέδου WARNING.

        Args:
            message (str): Το μήνυμα που θα καταγραφεί.
        """
        cls._logger.warning(message)

    @classmethod
    def error(cls, message: str) -> None:
        """
        Καταγράφει ένα μήνυμα επιπέδου ERROR.

        Args:
            message (str): Το μήνυμα που θα καταγραφεί.
        """
        cls._logger.error(message)


class LogOpject:
    def __init__(self, type_log: str):
        self.type_log = type_log

    def __call__(self, func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Πιάσε frame για την κλήση
            frame = sys._getframe(1)  # noqa: F841
            method_name = func.__name__.replace("_", " ").title()
            module_name = func.__module__

            # Αρχικοποίηση Logger
            LoggerManager.initialize()
            message = (
                f"[{self.type_log.upper()}] {module_name}.{method_name} εκτελέστηκε"
            )

            # Καταγραφή
            if self.type_log.lower() == "info":
                LoggerManager.info(message)
            elif self.type_log.lower() == "warning":
                LoggerManager.warning(message)
            elif self.type_log.lower() == "error":
                LoggerManager.error(message)

            # Εκτέλεση της αρχικής συνάρτησης
            return func(*args, **kwargs)

        return wrapper
