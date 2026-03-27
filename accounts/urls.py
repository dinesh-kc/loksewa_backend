# accounts/urls.py
from django.urls import path
from .views import register_view
from . import views

urlpatterns = [
    path('register/', register_view, name='register'),
    path('about/', views.about_page, name='about'),
    path('contact/', views.contact_page, name='contact'),
    path('privacy-policy/', views.privacy_policy, name='privacy_policy'),
    path('terms-of-service/', views.terms_of_service, name='terms_of_service'),
]