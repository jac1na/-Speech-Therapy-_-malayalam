# speech/urls.py
from django.urls import path
from .views import (
    UploadSpeechView, SpeechHistoryView, SpeechDetailView,
    ExerciseListView, ExerciseDetailView,
    PronunciationSubmitView, ResultListView, ResultDetailView,
    TodayPlanView, RecommendedExercisesView,
)

urlpatterns = [
    path('upload/', UploadSpeechView.as_view()),
    path('history/', SpeechHistoryView.as_view()),
    path('history/<int:pk>/', SpeechDetailView.as_view()),

    path('exercises/', ExerciseListView.as_view()),
    path('exercises/<int:pk>/', ExerciseDetailView.as_view()),
    path('pronunciation/', PronunciationSubmitView.as_view()),
    path('results/', ResultListView.as_view()),
    path('results/<int:pk>/', ResultDetailView.as_view()),
    path('plan/today/', TodayPlanView.as_view()),
    path('recommendations/', RecommendedExercisesView.as_view()),
]