# speech/services/scoring_service.py

class ScoringService:
    @staticmethod
    def calculate(comparison_result):
        total = comparison_result["total_words"]
        correct = comparison_result["correct_words"]

        if total == 0:
            return 0.0

        accuracy = (correct / total) * 100
        return round(accuracy, 2)