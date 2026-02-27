# from django.urls import path
# from .views import EnrollCourseView

# urlpatterns = [
#     path('', EnrollCourseView.as_view(), name='enroll-course'),
# ]

from django.urls import path
from . import views

urlpatterns = [
path('start/<int:course_id>/', views.start_enrollment, name='start_enrollment')
]