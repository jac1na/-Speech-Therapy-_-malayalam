from django.urls import path
from .views import UploadSpeechView, SpeechHistoryView, SpeechDetailView
from .views import (
    UploadSpeechView, SpeechHistoryView, SpeechDetailView,
    ExerciseListView, ExerciseDetailView,
    PronunciationSubmitView, ResultListView, ResultDetailView,
)

urlpatterns = [
    path('upload/', UploadSpeechView.as_view(), name='upload'),
    path('history/', SpeechHistoryView.as_view(), name='history'),
    path('history/<int:pk>/', SpeechDetailView.as_view(), name='history_detail'),
    path('exercises/', ExerciseListView.as_view(), name='exercises'),
    path('exercises/<int:pk>/', ExerciseDetailView.as_view(), name='exercise_detail'),
    path('pronunciation/', PronunciationSubmitView.as_view(), name='pronunciation'),
    path('results/', ResultListView.as_view(), name='results'),
    path('results/<int:pk>/', ResultDetailView.as_view(), name='result_detail'),
]