# from django.urls import path, include
# from rest_framework.routers import DefaultRouter
# from .views import CourseViewSet,SubjectViewSet, UnitViewSet, TopicViewSet

# router = DefaultRouter()
# router.register(r'courses', CourseViewSet, basename='course')
# router.register(r'subjects', SubjectViewSet, basename='subject')
# router.register(r'units', UnitViewSet, basename='unit')
# router.register(r'topics', TopicViewSet, basename='topic')

# urlpatterns = [
#     path('', include(router.urls)),
# ]

from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('course/<int:course_id>/', views.course_detail, name='course_detail'),
    path('topic/<int:topic_id>/', views.topic_detail, name='topic_detail'),
]