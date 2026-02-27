from django.shortcuts import render, get_object_or_404
from .models import Course, Topic
from django.utils import timezone
from django.contrib.auth.decorators import login_required


from django.http import JsonResponse
from mcq.models import Question, Bookmark

from enrollments.models import Enrollment

def home_view(request):
    if request.user.is_authenticated:
        # 1. Courses the user is already enrolled in
        enrolled_courses = Enrollment.objects.filter(user=request.user, is_active=True)
        # 2. Courses the user hasn't joined yet
        enrolled_ids = enrolled_courses.values_list('course_id', flat=True)
        available_courses = Course.objects.filter(is_active=True).exclude(id__in=enrolled_ids)
    
        return render(request, 'dashboard/student_dashboard.html', {
            'enrolled_courses': enrolled_courses,
            'available_courses': available_courses
        })
    else:
        # Guest View: SEO focused
        all_courses = Course.objects.filter(is_active=True)[:6]
        return render(request, 'landing/guest_home.html', {
            'courses': all_courses
        })

def course_list(request):
    courses = Course.objects.filter(is_active=True)
    return render(request, 'courses/course_list.html', {'courses': courses})

def course_detail(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    subjects = course.subject_set.all().prefetch_related('unit_set__topic_set')
    
    enrollment = None
    is_access_granted = False
    status_message = ""

    if request.user.is_authenticated:
        # Check if enrollment exists
        enrollment = Enrollment.objects.filter(user=request.user, course=course).first()
        
        if enrollment:
            # Check if expired
            if enrollment.expiry_date and enrollment.expiry_date < timezone.now():
                is_access_granted = False
                status_message = "EXPIRED"
            else:
                is_access_granted = True
                status_message = "TRIAL" if enrollment.is_trial else "ACTIVE"

    return render(request, 'courses/course_detail.html', {
        'course': course,
        'subjects': subjects,
        'enrollment': enrollment,
        'is_access_granted': is_access_granted,
        'status_message': status_message,
    })

def topic_detail(request, topic_id):
    topic = get_object_or_404(Topic, id=topic_id)
    return render(request, 'courses/topic_detail.html', {'topic': topic})









# from rest_framework import viewsets
# from rest_framework.permissions import IsAuthenticated,AllowAny
# from .models import Subject, Unit, Topic,Course
# from .serializers import SubjectSerializer, UnitSerializer, TopicSerializer,CourseSerializer

# class CourseViewSet(viewsets.ReadOnlyModelViewSet):
#     """
#     List and retrieve courses
#     """
#     queryset = Course.objects.all()
#     serializer_class = CourseSerializer
#     # permission_classes = [IsAuthenticated]  # Only authenticated users can access
#     permission_classes = [AllowAny]


# class SubjectViewSet(viewsets.ReadOnlyModelViewSet):
#     serializer_class = SubjectSerializer
#     permission_classes = [IsAuthenticated]

#     def get_queryset(self):
#         course_id = self.request.query_params.get('course')
#         queryset = Subject.objects.all()
#         if course_id:
#             queryset = queryset.filter(course_id=course_id)
#         return queryset.order_by('order')

# class UnitViewSet(viewsets.ReadOnlyModelViewSet):
#     serializer_class = UnitSerializer
#     permission_classes = [IsAuthenticated]

#     def get_queryset(self):
#         subject_id = self.request.query_params.get('subject')
#         queryset = Unit.objects.all()
#         if subject_id:
#             queryset = queryset.filter(subject_id=subject_id)
#         return queryset.order_by('order')

# class TopicViewSet(viewsets.ReadOnlyModelViewSet):
#     serializer_class = TopicSerializer
#     permission_classes = [IsAuthenticated]

#     def get_queryset(self):
#         unit_id = self.request.query_params.get('unit')
#         queryset = Topic.objects.all()
#         if unit_id:
#             queryset = queryset.filter(unit_id=unit_id)
#         return queryset.order_by('order')