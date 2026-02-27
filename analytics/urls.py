from django.urls import path
from .views import LeaderboardView, MyProgressView

urlpatterns = [
    path("leaderboard/", LeaderboardView.as_view(), name="leaderboard"),
    path("my-progress/", MyProgressView.as_view(), name="my-progress"),
]