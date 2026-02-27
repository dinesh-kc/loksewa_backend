from rest_framework import serializers
from .models import UserStats, TopicProgress


class LeaderboardSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username")

    average_score = serializers.SerializerMethodField()

    class Meta:
        model = UserStats
        fields = [
            "username",
            "total_score",
            "total_quizzes",
            "average_score",
        ]

    def get_average_score(self, obj):
        if obj.total_quizzes > 0:
            return obj.total_score / obj.total_quizzes
        return 0
    


class TopicProgressSerializer(serializers.ModelSerializer):
    topic_title = serializers.CharField(source='topic.title', read_only=True)

    class Meta:
        model = TopicProgress
        fields = ['id', 'topic', 'topic_title', 'total_attempted', 'correct_count', 'accuracy']