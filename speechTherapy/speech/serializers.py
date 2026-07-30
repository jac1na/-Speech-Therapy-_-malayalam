# speech/serializers.py
from rest_framework import serializers
from .models import SpeechSession, Exercise, SessionResult  ,DailyPracticePlan


class SpeechSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = SpeechSession
        fields = ['id', 'audio', 'transcript', 'created_at', 'duration', 'status']
        read_only_fields = ['transcript', 'created_at', 'duration', 'status']


class ExerciseSerializer(serializers.ModelSerializer):
    completed = serializers.SerializerMethodField()

    class Meta:
        model = Exercise
        fields = ['id', 'title', 'sentence', 'difficulty', 'completed']

    def get_completed(self, obj):
        # only meaningful when a 'completed_ids' set is passed in via context
        completed_ids = self.context.get('completed_ids')
        if completed_ids is None:
            return None
        return obj.id in completed_ids


class SessionResultSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='pk')
    exercise_id = serializers.IntegerField(source='exercise.id')
    exercise_title = serializers.CharField(source='exercise.title')
    sentence = serializers.CharField(source='exercise.sentence')
    score = serializers.FloatField(source='pronunciation_score')
    details = serializers.JSONField(source='word_details')
    feedback = serializers.SerializerMethodField()

    class Meta:
        model = SessionResult
        fields = [
            'id', 'exercise_id', 'exercise_title', 'sentence',
            'score', 'status', 'feedback', 'details', 'created_at',
        ]

    def get_feedback(self, obj):
        return obj.ai_feedback or obj.feedback


class DailyPracticePlanSerializer(serializers.ModelSerializer):
    completed = serializers.SerializerMethodField()
    total = serializers.SerializerMethodField()
    exercises = serializers.SerializerMethodField()

    class Meta:
        model = DailyPracticePlan
        fields = ['completed', 'total', 'exercises']

    def get_total(self, obj):
        return obj.exercises.count()

    def get_completed(self, obj):
        return obj.completed_exercises.count()

    def get_exercises(self, obj):
        completed_ids = set(obj.completed_exercises.values_list('id', flat=True))
        serializer = ExerciseSerializer(
            obj.exercises.all(), many=True, context={'completed_ids': completed_ids}
        )
        return serializer.data