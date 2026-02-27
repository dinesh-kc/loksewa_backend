
from django.db import models
from accounts.models import User
from courses.models import Course
from datetime import timedelta
from django.utils import timezone

class Enrollment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    is_trial = models.BooleanField(default=False)
    start_date = models.DateTimeField(default=timezone.now)
    expiry_date = models.DateTimeField()
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ('user', 'course')

    def save(self, *args, **kwargs):
        if not self.expiry_date:
            if self.is_trial:
                self.expiry_date = timezone.now() + timedelta(days=self.course.trial_days)
        super().save(*args, **kwargs)