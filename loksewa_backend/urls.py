from django.urls import path, include
from rest_framework.routers import DefaultRouter
# from enrollments.views import EnrollmentViewSet
# from mcq.views import SubmitQuizView


from django.contrib import admin
from django.urls import path, include

urlpatterns = [
 path('admin/', admin.site.urls),
    path('', include('courses.urls')),       # Home page र Courses को लागि
    path('quiz/', include('mcq.urls')),      # MCQ र Quiz को लागि
    path('enroll/', include('enrollments.urls')), # Enrollment को लागि
    # path('accounts/', include('django.contrib.auth.urls')), # Login/Logout को लागि
    path('accounts/', include('accounts.urls')), # This line links your accounts app
    path('accounts/', include('django.contrib.auth.urls')),
]


# from rest_framework_simplejwt.views import (
#     TokenObtainPairView,
#     TokenRefreshView,
# )

# router = DefaultRouter()
# router.register(r'enrollments', EnrollmentViewSet)

# urlpatterns = [
#     # path('api/', include(router.urls)),
#     path('api/quiz/<int:topic_id>/', SubmitQuizView.as_view()),
#     path("api/", include("mcq.urls")),
#     path("api/", include("analytics.urls")),
#     path('api/', include('courses.urls')),        # Courses
#     path('api/accounts/', include('accounts.urls')),
#     path('api/enrollments/', include('enrollments.urls')),


#         # JWT auth endpoints
#     path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
#     path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),

# ]