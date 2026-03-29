from rest_framework import generics
from .serializers import RegisterSerializer
from .models import User

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer




# accounts/views.py
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.db.models import Count
from .forms import RegisterForm # तपाईंको Custom User भएमा
from django.contrib import messages

from courses.models import Course
from enrollments.models import Enrollment



def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            messages.success(request, "Registration successful! Please login.")
            return redirect('login')
    else:
        form = RegisterForm()
    return render(request, 'registration/register.html', {'form': form})



def about_page(request):
    return render(request, 'about.html')

def contact_page(request):
    return render(request, 'contact.html')

def privacy_policy(request):
    return render(request, 'privacy_policy.html')

def terms_of_service(request):
    return render(request, 'terms_of_service.html')



def loksewa_preparation(request):
    """Landing page for Loksewa preparation"""
    return render(request, 'loksewa_preparation.html')

def online_loksewa_class(request):
    """Landing page for online Loksewa classes — lists active courses from the database."""
    base_qs = (
        Course.objects.filter(is_active=True)
        .annotate(subject_count=Count("subject"))
        .order_by("-created_at")
    )
    enrolled_courses = Course.objects.none()
    browse_courses = base_qs

    if request.user.is_authenticated:
        enrolled_ids = list(
            Enrollment.objects.filter(user=request.user, is_active=True).values_list(
                "course_id", flat=True
            )
        )
        if enrolled_ids:
            enrolled_courses = base_qs.filter(id__in=enrolled_ids)
            browse_courses = base_qs.exclude(id__in=enrolled_ids)
        else:
            browse_courses = base_qs

    return render(
        request,
        "online_loksewa_class.html",
        {
            "enrolled_courses": enrolled_courses,
            "browse_courses": browse_courses,
        },
    )

def online_loksewa_mcq(request):
    """Landing page for online Loksewa MCQ practice"""
    return render(request, 'online_loksewa_mcq.html')