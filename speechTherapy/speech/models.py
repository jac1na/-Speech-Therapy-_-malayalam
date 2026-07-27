

# Create your models here.
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
# speech/models.py (add below SpeechSession)

class Exercise(models.Model):
    title = models.CharField(max_length=100)
    sentence = models.TextField()  # Malayalam sentence, e.g. "മുയൽ വേഗം ഓടുന്നു"
    difficulty = models.CharField(max_length=20, default="easy")

    def __str__(self):
        return self.title


class SessionResult(models.Model):
    session = models.OneToOneField(SpeechSession, on_delete=models.CASCADE)
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE)
    pronunciation_score = models.FloatField()
    accuracy_score = models.FloatField()
    correct_words = models.IntegerField()
    incorrect_words = models.IntegerField()
    feedback = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)