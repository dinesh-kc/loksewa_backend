from rest_framework import serializers
from .models import Question, Choice, QuizAttempt, Answer
import random

class ChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Choice
        fields = ['id', 'option_text']


class QuestionSerializer(serializers.ModelSerializer):
    choices = serializers.SerializerMethodField()

    class Meta:
        model = Question
        fields = ['id', 'question_text', 'choices']

    def get_choices(self, obj):
        choices = obj.choices.all()
        return ChoiceSerializer(choices, many=True).data