# enrollment/utils.py
from django.utils import timezone
from .models import Enrollment

def has_active_enrollment(user, course):
    return Enrollment.objects.filter(
        user=user, 
        course=course, 
        is_active=True, 
        expiry_date__gt=timezone.now()
    ).exists()