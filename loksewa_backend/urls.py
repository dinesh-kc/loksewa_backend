from django.urls import path, include
from rest_framework.routers import DefaultRouter
# from enrollments.views import EnrollmentViewSet
# from mcq.views import SubmitQuizView


from django.contrib import admin
from django.urls import path, include
from public_quiz.admin_views import export_quiz_results
from django.views.generic import TemplateView
from accounts.views import loksewa_preparation, online_loksewa_class, online_loksewa_mcq

from django.contrib.sitemaps.views import sitemap
from .sitemap import StaticViewSitemap  # import your sitemaps

sitemaps = {
    'static': StaticViewSitemap,
    # 'articles': ArticleSitemap,  # if you have articles
}



urlpatterns = [
 path('admin/', admin.site.urls),
  path('admin/export-quiz-results/', export_quiz_results, name='admin_export_quiz_results'),
    path('', include('courses.urls')),       # Home page र Courses को लागि
    path('quiz/', include('mcq.urls')),      # MCQ र Quiz को लागि
    path('enroll/', include('enrollments.urls')), # Enrollment को लागि
    path('public_quiz/', include('public_quiz.urls')), # Enrollment को लागि
    # path('accounts/', include('django.contrib.auth.urls')), # Login/Logout को लागि
    path('accounts/', include('accounts.urls')), # This line links your accounts app
    path('accounts/', include('django.contrib.auth.urls')),

    # New SEO Landing Pages
    path('loksewa-preparation/', loksewa_preparation, name='loksewa_preparation'),
    path('online-loksewa-class/', online_loksewa_class, name='online_loksewa_class'),
    path('online-loksewa-mcq/', online_loksewa_mcq, name='online_loksewa_mcq'),
     path('robots.txt', TemplateView.as_view(template_name='robots.txt', content_type='text/plain')),

        path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
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