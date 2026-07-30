# speech/views.py
import threading
from rest_framework import generics, permissions
from rest_framework.response import Response

from .models import SpeechSession, Exercise, SessionResult, WordErrorLog, DailyPracticePlan
from .serializers import (
    SpeechSessionSerializer,
    ExerciseSerializer,
    SessionResultSerializer,
    DailyPracticePlanSerializer,
)
from .services.ffmpeg_service import FFmpegService
from .services.whisper_service import WhisperService
from .services.pronunciation_service import PronunciationService
from .services.scoring_service import ScoringService
from .services.feedback_service import FeedbackService
from .services.recommendation_service import RecommendationService
from .services.plan_service import PlanService


# ---------- Phase 1: plain upload + history ----------

class UploadSpeechView(generics.CreateAPIView):
    serializer_class = SpeechSessionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        instance = serializer.save(user=self.request.user)
        threading.Thread(target=self._process, args=(instance,)).start()

    def _process(self, instance):
        try:
            wav_path = FFmpegService.to_wav_16k_mono(instance.audio.path)
            transcript, duration = WhisperService.transcribe(wav_path)
            instance.transcript = transcript
            instance.duration = duration
            instance.status = "done"
            instance.save()
        except Exception as e:
            instance.status = "failed"
            instance.save()
            print(f"Processing error: {e}")


class SpeechHistoryView(generics.ListAPIView):
    serializer_class = SpeechSessionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return SpeechSession.objects.filter(user=self.request.user).order_by('-created_at')


class SpeechDetailView(generics.RetrieveAPIView):
    serializer_class = SpeechSessionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return SpeechSession.objects.filter(user=self.request.user)


# ---------- Phase 2/3: exercises ----------

class ExerciseListView(generics.ListAPIView):
    queryset = Exercise.objects.all()
    serializer_class = ExerciseSerializer
    permission_classes = [permissions.IsAuthenticated]


class ExerciseDetailView(generics.RetrieveAPIView):
    queryset = Exercise.objects.all()
    serializer_class = ExerciseSerializer
    permission_classes = [permissions.IsAuthenticated]


class RecommendedExercisesView(generics.ListAPIView):
    serializer_class = ExerciseSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return RecommendationService.recommend_exercises(self.request.user)


# ---------- Phase 2/3: pronunciation submission + results ----------

class PronunciationSubmitView(generics.CreateAPIView):
    """
    multipart form-data: audio (file), exercise_id (int)
    Returns {"id": <result_id>} immediately; frontend polls /api/results/<id>/.
    """
    serializer_class = SpeechSessionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        exercise_id = request.data.get("exercise_id")
        exercise = Exercise.objects.get(id=exercise_id)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        session = serializer.save(user=request.user)

        result = SessionResult.objects.create(
            session=session, exercise=exercise, status="pending"
        )

        threading.Thread(target=self._process, args=(session, exercise, result)).start()

        return Response({"id": result.pk}, status=201)

    def _process(self, session, exercise, result):
        try:
            result.status = "processing"
            result.save()

            wav_path = FFmpegService.to_wav_16k_mono(session.audio.path)
            transcript, duration = WhisperService.transcribe(wav_path)
            session.transcript = transcript
            session.duration = duration
            session.status = "done"
            session.save()

            comparison = PronunciationService.compare(exercise.sentence, transcript)
            score = ScoringService.calculate(comparison)
            feedback = FeedbackService.generate(score)

            for w in comparison["word_details"]:
                if not w["correct"]:
                    try:
                        WordErrorLog.objects.create(
                            user=session.user, expected_word=w["word"], recognized_word=""
                        )
                    except Exception as exc:
                        print(f"WordErrorLog creation failed: {exc}")

            result.pronunciation_score = score
            result.accuracy_score = score
            result.correct_words = comparison["correct_words"]
            result.incorrect_words = comparison["incorrect_words"]
            result.word_details = comparison["word_details"]
            result.feedback = feedback
            result.status = "done"
            result.save()

        except Exception as e:
            result.status = "failed"
            result.save()
            session.status = "failed"
            session.save()
            print(f"Processing error: {e}")


class ResultListView(generics.ListAPIView):
    serializer_class = SessionResultSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return SessionResult.objects.filter(session__user=self.request.user).order_by('-created_at')


class ResultDetailView(generics.RetrieveAPIView):
    serializer_class = SessionResultSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return SessionResult.objects.filter(session__user=self.request.user)


# ---------- Phase 3: daily plan ----------

class TodayPlanView(generics.RetrieveAPIView):
    serializer_class = DailyPracticePlanSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return PlanService.get_or_create_today_plan(self.request.user)