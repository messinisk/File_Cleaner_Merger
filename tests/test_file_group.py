import unittest
from core import FileGroup
from core import File
from unittest.mock import MagicMock
import os

mock_file1 = MagicMock()
mock_file1.content = "xyz"

class TestFileGroup(unittest.TestCase):

    def setUp(self):
        self.files = []
        for i in range(2):
            name = f"temp{i}.txt"
            with open(name, "w") as f:
                f.write("Hello world")
            self.files.append(File(name))
        self.group = FileGroup()

    def tearDown(self):
        for f in self.files:
            os.remove(f.path)

    def test_add_file_increases_count(self):
        self.group.add_file(self.files[0])
        self.assertEqual(len(self.group.files), 1)

    def test_similarity_score_returns_float(self):
        self.group.add_file(self.files[0])
        score = self.group.similarity_score(self.files[1])
        self.assertIsInstance(score, float)
    
    def test_similarity_score_empty(self):
        group = FileGroup(files=[])
        assert group.similarity_score("whatever") == 0.0

    def test_similarity_score_with_mock(self):
        # δημιουργούμε "ψεύτικο" αρχείο με πεδίο .content
        mock_file_1 = MagicMock()
        mock_file_1.content = "abc"
        
        mock_other_file = MagicMock()
        mock_other_file.content = "def"

        group = FileGroup(files=[mock_file_1])

        # κάνουμε mock τη μέθοδο που υπολογίζει ομοιότητα
        group._calculate_similarity = MagicMock(return_value=0.75)  # type: ignore

        result = group.similarity_score(mock_other_file)

        assert isinstance(result, float)
        assert 0 <= result <= 1


if __name__ == "__main__":
    unittest.main()
