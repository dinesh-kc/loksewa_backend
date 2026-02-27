from rest_framework.generics import ListAPIView
from .models import TopicProgress,UserStats
from .serializers import TopicProgressSerializer
from rest_framework.permissions import IsAuthenticated

from .serializers import LeaderboardSerializer

class MyProgressView(ListAPIView):
    serializer_class = TopicProgressSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return TopicProgress.objects.filter(user=self.request.user)
    


class LeaderboardView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = LeaderboardSerializer

    def get_queryset(self):
        return UserStats.objects.all().order_by("-total_score")[:50]