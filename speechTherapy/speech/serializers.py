from rest_framework import serializers
from .models import SpeechSession
from .models import Exercise, SessionResult


class SpeechSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = SpeechSession
        fields = ['id', 'audio', 'transcript', 'created_at', 'duration']
        read_only_fields = ['transcript', 'created_at', 'duration']

class ExerciseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Exercise
        fields = ['id', 'title', 'sentence', 'difficulty']


class SessionResultSerializer(serializers.ModelSerializer):
    exercise = ExerciseSerializer(read_only=True)

    class Meta:
        model = SessionResult
        fields = [
            'id', 'session', 'exercise', 'pronunciation_score',
            'accuracy_score', 'correct_words', 'incorrect_words',
            'feedback', 'created_at'
        ]