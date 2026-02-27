from rest_framework.views import APIView


from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from courses.models import Course
from .models import Enrollment
from datetime import timedelta
from django.contrib import messages
from django.utils import timezone

@login_required
def start_enrollment(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    
    # Check if already enrolled
    enrollment, created = Enrollment.objects.get_or_create(
        user=request.user, 
        course=course,
        defaults={
            'is_active': True,
            'is_trial': not course.is_free,
            'expiry_date': timezone.now() + timedelta(days=36500) if course.is_free else None 
            # Note: If is_trial is True, your Model's save() method will auto-calculate expiry_date
        }
    )

    if created:
        if course.is_free:
            messages.success(request, f"You now have Lifetime Access to {course.title}!")
        else:
            messages.success(request, f"Your {course.trial_days}-day trial has started!")
    else:
        messages.info(request, "You are already enrolled in this course.")

    return redirect('course_detail', course_id=course.id)





# from rest_framework.response import Response
# from rest_framework.permissions import IsAuthenticated
# from .serializers import EnrollmentSerializer

# from .models import Enrollment
# from courses.models import Course

# class EnrollCourseView(APIView):
#     permission_classes = [IsAuthenticated]

#     def get(self, request):
#         """Get all enrollments for the authenticated user"""
#         try:
#             # Get all enrollments for the current user
#             enrollments = Enrollment.objects.filter(
#                 user=request.user,
#                 is_active=True
#             ).select_related('course').order_by('-start_date')
            
#             # Serialize the data
#             serializer = EnrollmentSerializer(enrollments, many=True)
            
#             return Response({
#                 "status": "success",
#                 "data": serializer.data
#             }, status=200)
            
#         except Exception as e:
#             return Response({
#                 "status": "error",
#                 "message": str(e)
#             }, status=500)

#     def post(self, request):
#         course_id = request.data.get('course_id')
#         course = Course.objects.get(id=course_id)
#         print(course)

#         # Free Course → direct enrollment
#         if course.is_free:
#             Enrollment.objects.get_or_create(
#                 user=request.user,
#                 course=course,
#                 is_trial=False
#             )
#             return Response({"message": "Enrolled in free course successfully"})

#         # Trial Course
#         if course.is_trial_available:
#             Enrollment.objects.get_or_create(
#                 user=request.user,
#                 course=course,
#                 is_trial=True
#             )
#             return Response({"message": f"Trial started for {course.trial_days} days"})

#         # Paid Course
#         return Response({
#             "message": "This is a paid course. Please contact admin at 98XXXXXXXX to purchase."
#         })