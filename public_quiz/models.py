import uuid
from django.db import models
from django.utils.text import slugify
from django.urls import reverse
from courses.models import Topic
from django.utils import timezone
from mcq.models import Question, Choice  # existing

# -------------------------
# Public Quiz
# -------------------------
class PublicQuiz(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    slug = models.SlugField(unique=True, blank=True)
    topic = models.ForeignKey(Topic, on_delete=models.SET_NULL, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    time_limit = models.PositiveIntegerField(
        default=30, 
        help_text="Time limit in minutes for the entire quiz"
    )
    start_time = models.DateTimeField(null=True, blank=True, 
                                       help_text="Scheduled start time for the quiz")
    end_time = models.DateTimeField(null=True, blank=True,
                                     help_text="Scheduled end time for the quiz")

    def save(self, *args, **kwargs):
        if not self.slug:
            # Create a slug from title
            base_slug = slugify(self.title)
            if not base_slug:  # If title doesn't create a slug (e.g., special chars)
                base_slug = str(uuid.uuid4())[:8]
            
            # Check uniqueness
            slug = base_slug
            counter = 1
            while PublicQuiz.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        """Returns the relative URL for the quiz"""
        return reverse('public_quiz:info', kwargs={'slug': self.slug})

    def get_full_url(self, request=None):
        """Returns full URL with domain"""
        if request:
            return request.build_absolute_uri(self.get_absolute_url())
        return self.get_absolute_url()

    def __str__(self):
        return self.title
    
    def is_available_now(self):
        """Check if quiz is available based on start/end times"""
        now = timezone.now()
        if self.start_time and now < self.start_time:
            return False
        if self.end_time and now > self.end_time:
            return False
        return True

    class Meta:
        verbose_name = "Public Quiz"
        verbose_name_plural = "Public Quizzes"
        ordering = ['-created_at']


class PublicQuizQuestion(models.Model):
    quiz = models.ForeignKey(PublicQuiz, on_delete=models.CASCADE, related_name='quiz_questions')
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='public_quizzes')
    order = models.PositiveIntegerField(default=0, help_text="Order of question in quiz")

    class Meta:
        ordering = ['order']
        unique_together = ['quiz', 'question']  # Prevent duplicate questions

    def __str__(self):
        return f"{self.quiz.title} - Q{self.order}"


class PublicAttempt(models.Model):
    quiz = models.ForeignKey(PublicQuiz, on_delete=models.CASCADE, related_name='attempts')
    name = models.CharField(max_length=100)
    email = models.EmailField()
    mobile = models.CharField(max_length=20)
    
    score = models.FloatField(default=0)
    total_questions = models.IntegerField(default=0)
    correct_answers = models.IntegerField(default=0)
    wrong_answers = models.IntegerField(default=0)
    
    session_key = models.CharField(max_length=40, blank=True, null=True)
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.name} - {self.quiz.title}"

    class Meta:
        ordering = ['-completed_at']


class PublicAnswer(models.Model):
    attempt = models.ForeignKey(PublicAttempt, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_choice = models.ForeignKey(Choice, on_delete=models.CASCADE, null=True, blank=True)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.attempt.name} - Q{self.question.id}"