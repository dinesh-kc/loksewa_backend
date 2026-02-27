import json
from django.contrib import admin, messages
from django.shortcuts import render, redirect
from django.urls import path
from django import forms
from .models import Question, Choice, Topic

class JsonImportForm(forms.Form):
    json_file = forms.FileField()

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('question_text', 'topic', 'difficulty')
    change_list_template = "admin/mcq_question_changelist.html" # Custom button thapna

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path('import-json/', self.import_json, name="import_json"),
        ]
        return my_urls + urls

    def import_json(self, request):
        if request.method == "POST":
            json_file = request.FILES["json_file"]
            data = json.load(json_file)
            
            created_count = 0
            for item in data:
                try:
                    # 1. Question Create garne
                    topic = Topic.objects.get(id=item['topic_id'])
                    question = Question.objects.create(
                        topic=topic,
                        question_text=item['question_text'],
                        difficulty=item.get('difficulty', 'MEDIUM'),
                        explanation=item.get('explanation', ''),
                    )
                    
                    # 2. Choices Create garne
                    for choice_data in item['choices']:
                        Choice.objects.create(
                            question=question,
                            option_text=choice_data['text'],
                            is_correct=choice_data['is_correct']
                        )
                    created_count += 1
                except Exception as e:
                    self.message_user(request, f"Error importing: {str(e)}", messages.ERROR)

            self.message_user(request, f"Successfully imported {created_count} questions.")
            return redirect("..")

        form = JsonImportForm()
        return render(request, "admin/json_form.html", {"form": form})