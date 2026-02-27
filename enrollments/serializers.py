# enrollments/serializers.py
from rest_framework import serializers
from .models import Enrollment
from courses.models import Course
from courses.serializers import CourseSerializer

class EnrollmentSerializer(serializers.ModelSerializer):
    course = CourseSerializer(read_only=True)
    days_left = serializers.SerializerMethodField()
    
    class Meta:
        model = Enrollment
        fields = ['id', 'course', 'is_trial', 'start_date', 'expiry_date', 'is_active', 'days_left']
    
    def get_days_left(self, obj):
        if obj.expiry_date:
            days = (obj.expiry_date - obj.start_date).days
            return max(0, days)
        return None