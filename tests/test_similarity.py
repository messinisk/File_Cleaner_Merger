import unittest
from core.similarity import FileSimilarity
from types import SimpleNamespace

def test_suggest_pairs_with_thresholds():
    file1 = SimpleNamespace(name="a.txt", content="hello world")
    file2 = SimpleNamespace(name="b.txt", content="hello world")
    file3 = SimpleNamespace(name="c.txt", content="completely different text")

    files = [file1, file2, file3]

    # Περίπτωση 1: threshold χαμηλό → πιάνει όμοια αρχεία
    pairs = FileSimilarity.suggest_pairs(files, threshold=0.5) # type: ignore
    assert any(p["file_a"] == "a.txt" and p["file_b"] == "b.txt" for p in pairs)
    assert all("score" in p for p in pairs)

    # Περίπτωση 2: threshold πολύ υψηλό για να κόψει τα πάντα (π.χ. > 1)
    no_pairs = FileSimilarity.suggest_pairs(files, threshold=1.01) # type: ignore
    assert no_pairs == []

    # Περίπτωση 3: λίστα με 1 αρχείο → δεν υπάρχουν συνδυασμοί
    single_pair = FileSimilarity.suggest_pairs([file1], threshold=0.5) # type: ignore
    assert single_pair == []


if __name__ == "__main__":
    unittest.main()
# tests/test_similarity.py