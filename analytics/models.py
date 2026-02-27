from django.db import models
from accounts.models import User
from courses.models import Topic

class TopicProgress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE)
    total_attempted = models.IntegerField(default=0)
    correct_count = models.IntegerField(default=0)
    accuracy = models.FloatField(default=0)

    class Meta:
        unique_together = ('user', 'topic')

    def update_accuracy(self):
        if self.total_attempted > 0:
            self.accuracy = (self.correct_count / self.total_attempted) * 100
        else:
            self.accuracy = 0
        self.save()


class UserStats(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    total_score = models.FloatField(default=0)
    total_quizzes = models.IntegerField(default=0)

    def average_score(self):
        if self.total_quizzes > 0:
            return self.total_score / self.total_quizzes
        return 0