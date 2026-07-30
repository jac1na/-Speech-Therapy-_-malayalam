# speech/services/plan_service.py
from datetime import date
from ..models import DailyPracticePlan
from .recommendation_service import RecommendationService


class PlanService:
    @staticmethod
    def get_or_create_today_plan(user, exercise_count=5):
        plan, created = DailyPracticePlan.objects.get_or_create(
            user=user,
            date=date.today(),
        )
        if created:
            exercises = RecommendationService.recommend_exercises(user, count=exercise_count)
            plan.exercises.set(exercises)
        return plan