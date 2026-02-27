
from django.db import models
from courses.models import Topic
from accounts.models import User
from django.utils import timezone
from datetime import timedelta

class Question(models.Model):

    DIFFICULTY = (
        ('EASY', 'Easy'),
        ('MEDIUM', 'Medium'),
        ('HARD', 'Hard'),
    )

    topic = models.ForeignKey(Topic, on_delete=models.CASCADE)
    question_text = models.TextField()
    difficulty = models.CharField(max_length=10, choices=DIFFICULTY)
    marks = models.IntegerField(default=1)
    negative_marks = models.FloatField(default=0)
    explanation = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)


class Choice(models.Model):
    question = models.ForeignKey(Question, related_name="choices", on_delete=models.CASCADE)
    option_text = models.CharField(max_length=300)
    is_correct = models.BooleanField(default=False)



class QuizAttempt(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE)
    score = models.FloatField(default=0)
    total_questions = models.IntegerField()
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)


class Answer(models.Model):
    attempt = models.ForeignKey(QuizAttempt, related_name="answers", on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_choice = models.ForeignKey(Choice, on_delete=models.CASCADE)
    is_correct = models.BooleanField()

class Bookmark(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'question')



class SpacedRevision(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    # 1: Easy, 2: Medium, 3: Hard (Hami interval optimize garna sakchaun)
    interval = models.IntegerField(default=1) # Din ma
    easiness_factor = models.FloatField(default=2.5)
    next_review = models.DateTimeField(default=timezone.now)
    is_mastered = models.BooleanField(default=False)

    class Meta:
        unique_together = ('user', 'question')

    def __str__(self):
        return f"{self.user.username} - {self.question.id}"
