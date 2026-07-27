from django.shortcuts import render

# Create your views here.
from rest_framework import generics, permissions
from .models import SpeechSession
from .serializers import SpeechSessionSerializer
from .services.whisper_service import WhisperService
from .services.ffmpeg_service import FFmpegService
from .models import Exercise, SessionResult
from .serializers import ExerciseSerializer, SessionResultSerializer
from .services.ffmpeg_service import FFmpegService
from .services.whisper_service import WhisperService
from .services.pronunciation_service import PronunciationService
from .services.scoring_service import ScoringService
from .services.feedback_service import FeedbackService


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

    # def perform_create(self, serializer):
    #     instance = serializer.save(user=self.request.user)
    #     transcript, duration = WhisperService.transcribe(instance.audio.path)
    #     instance.transcript = transcript
    #     instance.duration = duration
    #     instance.save()

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

# speech/views.py (add)



class ExerciseListView(generics.ListAPIView):
    queryset = Exercise.objects.all()
    serializer_class = ExerciseSerializer
    permission_classes = [permissions.IsAuthenticated]


class ExerciseDetailView(generics.RetrieveAPIView):
    queryset = Exercise.objects.all()
    serializer_class = ExerciseSerializer
    permission_classes = [permissions.IsAuthenticated]


class PronunciationSubmitView(generics.CreateAPIView):
    """
    Expects multipart form-data:
      - audio: file
      - exercise_id: int
    """
    serializer_class = SpeechSessionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        exercise_id = self.request.data.get("exercise_id")
        exercise = Exercise.objects.get(id=exercise_id)
        instance = serializer.save(user=self.request.user)
        threading.Thread(
            target=self._process, args=(instance, exercise)
        ).start()

    def _process(self, instance, exercise):
        try:
            wav_path = FFmpegService.to_wav_16k_mono(instance.audio.path)
            transcript, duration = WhisperService.transcribe(wav_path)
            instance.transcript = transcript
            instance.duration = duration
            instance.status = "done"
            instance.save()

            comparison = PronunciationService.compare(exercise.sentence, transcript)
            score = ScoringService.calculate(comparison)
            feedback = FeedbackService.generate(score)

            SessionResult.objects.create(
                session=instance,
                exercise=exercise,
                pronunciation_score=score,
                accuracy_score=score,
                correct_words=comparison["correct_words"],
                incorrect_words=comparison["incorrect_words"],
                feedback=feedback,
            )
        except Exception as e:
            instance.status = "failed"
            instance.save()
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