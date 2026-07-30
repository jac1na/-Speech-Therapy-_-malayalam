# speech/services/pronunciation_service.py
import re
import difflib

class PronunciationService:
    @staticmethod
    def normalize_word(w):
        return re.sub(r"[।.,!?;:\"'()]", "", w).strip()

    @staticmethod
    def compare(expected_text, recognized_text):
        expected_words = [PronunciationService.normalize_word(w) for w in expected_text.split()]
        recognized_words = [PronunciationService.normalize_word(w) for w in recognized_text.split()]

        matcher = difflib.SequenceMatcher(None, expected_words, recognized_words)
        word_details = []  # full per-word list, in expected-sentence order
        correct = 0

        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag == "equal":
                for w in expected_words[i1:i2]:
                    word_details.append({"word": w, "correct": True})
                correct += (i2 - i1)
            else:
                for w in expected_words[i1:i2]:
                    word_details.append({"word": w, "correct": False})

        total = len(expected_words)
        incorrect = total - correct

        return {
            "total_words": total,
            "correct_words": correct,
            "incorrect_words": incorrect,
            "word_details": word_details,
        }