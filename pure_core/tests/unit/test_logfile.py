import unittest
from unittest.mock import MagicMock, patch
import logging
from pure_core.logfile import LoggerManager


class TestLoggerManager(unittest.TestCase):

    def setUp(self):
        # Reset logger πριν από κάθε τεστ
        LoggerManager._logger = None # pyright: ignore[reportAttributeAccessIssue]

    @patch("logging.getLogger")
    @patch("logging.basicConfig")
    def test_initialize_creates_logger(self, mock_basicConfig, mock_getLogger):
        mock_logger = MagicMock()
        mock_getLogger.return_value = mock_logger

        LoggerManager.initialize("test.log", logging.DEBUG)

        mock_basicConfig.assert_called_once_with(
            filename="test.log",
            level=logging.DEBUG,
            format="%(asctime)s - %(levelname)s - %(message)s",
        )
        mock_getLogger.assert_called_once_with("FileInspector")
        self.assertEqual(LoggerManager._logger, mock_logger)

    @patch("logging.getLogger")
    @patch("logging.basicConfig")
    def test_initialize_does_not_recreate_logger_if_exists(self, mock_basicConfig, mock_getLogger):
        # Δημιουργούμε ψεύτικο logger
        LoggerManager._logger = MagicMock()

        LoggerManager.initialize("should_not_create.log", logging.WARNING)

        # Δεν πρέπει να ξανακαλέσει basicConfig και getLogger
        mock_basicConfig.assert_not_called()
        mock_getLogger.assert_not_called()

    def test_info_calls_logger_info(self):
        mock_logger = MagicMock()
        LoggerManager._logger = mock_logger

        LoggerManager.info("test message")
        mock_logger.info.assert_called_once_with("test message")

    def test_warning_calls_logger_warning(self):
        mock_logger = MagicMock()
        LoggerManager._logger = mock_logger

        LoggerManager.warning("warn message")
        mock_logger.warning.assert_called_once_with("warn message")

    def test_error_calls_logger_error(self):
        mock_logger = MagicMock()
        LoggerManager._logger = mock_logger

        LoggerManager.error("error message")
        mock_logger.error.assert_called_once_with("error message")

if __name__ == "__main__":
    unittest.main()