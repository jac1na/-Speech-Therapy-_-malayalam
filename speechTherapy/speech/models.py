# speech/models.py
from django.db import models
from django.contrib.auth.models import User


class SpeechSession(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("done", "Done"),
        ("failed", "Failed"),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sessions')
    audio = models.FileField(upload_to='audio/')
    transcript = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    duration = models.FloatField(null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="pending")

    def __str__(self):
        return f"{self.user.username} - {self.created_at}"


class Exercise(models.Model):
    title = models.CharField(max_length=100)
    sentence = models.TextField()
    difficulty = models.CharField(max_length=20, default="easy")

    def __str__(self):
        return self.title


class SessionResult(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("processing", "Processing"),
        ("done", "Done"),
        ("failed", "Failed"),
    ]
    # primary_key=True makes result.id == session.id, so the frontend can poll
    # /api/results/<id>/ using the same id returned from /api/pronunciation/
    session = models.OneToOneField(SpeechSession, on_delete=models.CASCADE, primary_key=True)
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE)
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default="pending")
    pronunciation_score = models.FloatField(default=0)
    accuracy_score = models.FloatField(default=0)
    correct_words = models.IntegerField(default=0)
    incorrect_words = models.IntegerField(default=0)
    feedback = models.TextField(blank=True)
    ai_feedback = models.TextField(blank=True)
    word_details = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)


class WordErrorLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    expected_word = models.CharField(max_length=100)
    recognized_word = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)


class DailyPracticePlan(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)
    exercises = models.ManyToManyField(Exercise)
    completed_exercises = models.ManyToManyField(
        Exercise, related_name="completed_in_plans", blank=True
    )

    class Meta:
        unique_together = ('user', 'date')