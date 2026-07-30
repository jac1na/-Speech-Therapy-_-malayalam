# speech/services/recommendation_service.py
from collections import Counter
from ..models import WordErrorLog, Exercise


class RecommendationService:
    @staticmethod
    def get_weak_words(user, limit=5):
        try:
            logs = WordErrorLog.objects.filter(user=user).order_by('-created_at')[:100]
        except Exception as exc:
            print(f"Failed to load weak word history: {exc}")
            return []
        words = [log.expected_word for log in logs]
        counter = Counter(words)
        return [word for word, _ in counter.most_common(limit)]

    @staticmethod
    def recommend_exercises(user, count=5):
        weak_words = RecommendationService.get_weak_words(user)

        if not weak_words:
            return list(Exercise.objects.filter(difficulty="easy")[:count])

        exercises = Exercise.objects.all()
        scored = []
        for ex in exercises:
            overlap = sum(1 for w in weak_words if w in ex.sentence)
            if overlap > 0:
                scored.append((overlap, ex))

        scored.sort(key=lambda x: x[0], reverse=True)
        recommended = [ex for _, ex in scored[:count]]

        if len(recommended) < count:
            existing_ids = [ex.id for ex in recommended]
            fill = Exercise.objects.exclude(id__in=existing_ids)[:count - len(recommended)]
            recommended += list(fill)

        return recommended