from django.urls import path
from . import views

app_name = 'public_quiz'  # Add this for namespacing

urlpatterns = [
    path('quiz/<slug:slug>/', views.public_quiz_info, name='info'),
    path('quiz/<slug:slug>/take/', views.public_quiz_take, name='take'),
    path('quiz/<slug:slug>/result/', views.public_quiz_result, name='result'),
     path('quiz/<slug:slug>/waiting/', views.public_quiz_waiting, name='waiting'),
]