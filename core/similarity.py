import difflib
from typing import List
from core import File


class FileSimilarity:
    @staticmethod
    def similarity_score(content_a: str, content_b: str) -> float:
        """
        Υπολογίζει το ποσοστό ομοιότητας δύο περιεχομένων (0-1)
        βάσει γραμμής προς γραμμή.
        """
        a_lines = content_a.splitlines()
        b_lines = content_b.splitlines()
        seq = difflib.SequenceMatcher(None, a_lines, b_lines)
        return seq.ratio()  # 1.0 = ίδια, 0.0 = καθόλου κοινά

    @staticmethod
    def suggest_pairs(files: List["File"], threshold: float = 0.5):
        """
        Προτείνει ζεύγη αρχείων που έχουν similarity πάνω από το threshold.
        """
        suggestions = []
        n = len(files)
        for i in range(n):
            for j in range(i + 1, n):
                score = FileSimilarity.similarity_score(files[i].content, files[j].content)
                if score >= threshold:
                    suggestions.append({
                        "file_a": files[i].name,
                        "file_b": files[j].name,
                        "score": round(score, 2)
                    })
        return suggestions


