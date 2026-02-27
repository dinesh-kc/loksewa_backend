# from django.urls import path
# from .views import SubmitQuizView

# urlpatterns = [
#     path("quiz/submit/", SubmitQuizView.as_view(), name="submit-quiz"),
# ]

from django.urls import path
from . import views

urlpatterns = [
    path('start/<int:topic_id>/', views.start_quiz, name='start_quiz'),
    path('result/<int:attempt_id>/', views.quiz_result, name='quiz_result'),

    path('topic/<int:topic_id>/', views.topic_detail, name='topic_detail'),

    # 2. Toggle Bookmark (AJAX ko lagi - page refresh hudaina)
    path('bookmark/<int:question_id>/', views.toggle_bookmark, name='toggle_bookmark'),

    path('topic/<int:topic_id>/quiz/', views.quiz_mode, name='quiz_mode'),

    # 3. Daily Limit Reached (Trial user ko limit sakida dekhine page)
    path('daily-limit-reached/', views.daily_limit_reached, name='daily_limit'),

    path('bookmarks/', views.bookmark_list, name='bookmark_list'),
    path('bookmarks/course/<int:course_id>/', views.course_bookmarks, name='course_bookmarks'),
    path('revision/', views.daily_revision_quiz, name='daily_revision'),
]