# speech/services/pronunciation_service.py
import re
import difflib

class PronunciationService:
    @staticmethod
    def normalize(text):
        # Strip punctuation, extra whitespace, normalize to single spaces
        text = re.sub(r"[।.,!?;:\"'()]", "", text)
        text = re.sub(r"\s+", " ", text).strip()
        return text

    @staticmethod
    def compare(expected_text, recognized_text):
        expected_words = PronunciationService.normalize(expected_text).split()
        recognized_words = PronunciationService.normalize(recognized_text).split()

        matcher = difflib.SequenceMatcher(None, expected_words, recognized_words)
        correct = 0
        incorrect_details = []

        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag == "equal":
                correct += (i2 - i1)
            else:
                expected_chunk = expected_words[i1:i2]
                recognized_chunk = recognized_words[j1:j2]
                incorrect_details.append({
                    "expected": " ".join(expected_chunk) if expected_chunk else None,
                    "recognized": " ".join(recognized_chunk) if recognized_chunk else None,
                })

        total = len(expected_words)
        incorrect = total - correct

        return {
            "total_words": total,
            "correct_words": correct,
            "incorrect_words": incorrect,
            "details": incorrect_details,
        }