from rest_framework import generics
from .serializers import RegisterSerializer
from .models import User

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer




# accounts/views.py
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from .forms import RegisterForm # तपाईंको Custom User भएमा
from django.contrib import messages



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
    """Landing page for online Loksewa classes"""
    return render(request, 'online_loksewa_class.html')

def online_loksewa_mcq(request):
    """Landing page for online Loksewa MCQ practice"""
    return render(request, 'online_loksewa_mcq.html')