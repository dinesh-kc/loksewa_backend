from django.contrib import admin
from django.utils.html import format_html
from django.urls import path, reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.contrib import messages
from django import forms
from django.db.models import Max
import csv
from datetime import datetime
from .models import PublicQuiz, PublicQuizQuestion, PublicAttempt, PublicAnswer
from mcq.models import Question, Topic

class PublicQuizQuestionInline(admin.TabularInline):
    model = PublicQuizQuestion
    extra = 1
    raw_id_fields = ['question']
    ordering = ['order']

class BulkAddQuestionForm(forms.Form):
    topic = forms.ModelChoiceField(queryset=Topic.objects.all(), required=True, label="Select Topic")
    questions = forms.ModelMultipleChoiceField(
        queryset=Question.objects.none(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="Select Questions"
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'topic' in self.data:
            try:
                topic_id = int(self.data.get('topic'))
                self.fields['questions'].queryset = Question.objects.filter(topic_id=topic_id).order_by('id')
            except (ValueError, TypeError):
                pass

@admin.register(PublicQuiz)
class PublicQuizAdmin(admin.ModelAdmin):
    list_display = ['title', 'topic', 'is_active', 'question_count', 'attempt_count', 'created_at', 'display_quiz_link']
    list_filter = ['is_active', 'topic', 'created_at']
    search_fields = ('title', 'topic__name')
    prepopulated_fields = {'slug': ('title',)}
    inlines = [PublicQuizQuestionInline]
    readonly_fields = ['created_at']
    actions = ['bulk_add_questions_action', 'export_quiz_attempts']

    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description', 'topic', 'is_active')
        }),
        ('Timing Settings', {
            'fields': ('time_limit', 'start_time', 'end_time'),
            'classes': ('wide',),
            'description': 'Set time limit in minutes and optional scheduled start/end times'
        }),
        ('URL Settings', {
            'fields': ('slug',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('bulk-add-questions/<int:quiz_id>/',
                 self.admin_site.admin_view(self.bulk_add_questions_view),
                 name='public_quiz_bulk_add_questions'),
        ]
        return custom_urls + urls

    def bulk_add_questions_action(self, request, queryset):
        if queryset.count() != 1:
            messages.error(request, "Please select exactly one quiz to bulk add questions.")
            return
        quiz = queryset.first()
        return HttpResponseRedirect(
            reverse('admin:public_quiz_bulk_add_questions', args=[quiz.id])
        )
    bulk_add_questions_action.short_description = "Bulk add questions to selected quiz"

    def bulk_add_questions_view(self, request, quiz_id):
        quiz = get_object_or_404(PublicQuiz, id=quiz_id)

        if request.method == 'POST':
            form = BulkAddQuestionForm(request.POST)
            topic_id = request.POST.get('topic')
            if topic_id:
                form.fields['questions'].queryset = Question.objects.filter(topic_id=topic_id).order_by('id')
            if form.is_valid():
                questions = form.cleaned_data['questions']
                existing_ids = set(PublicQuizQuestion.objects.filter(quiz=quiz).values_list('question_id', flat=True))
                added = 0
                max_order = PublicQuizQuestion.objects.filter(quiz=quiz).aggregate(Max('order'))['order__max'] or 0
                for q in questions:
                    if q.id not in existing_ids:
                        max_order += 1
                        PublicQuizQuestion.objects.create(quiz=quiz, question=q, order=max_order)
                        added += 1
                messages.success(request, f"Added {added} questions to '{quiz.title}'.")
                return HttpResponseRedirect(reverse('admin:public_quiz_publicquiz_change', args=[quiz.id]))
            else:
                if topic_id:
                    form.fields['questions'].queryset = Question.objects.filter(topic_id=topic_id).order_by('id')
        else:
            form = BulkAddQuestionForm(request.GET or None)
            topic_id = request.GET.get('topic')
            if topic_id:
                form.fields['questions'].queryset = Question.objects.filter(topic_id=topic_id).order_by('id')
                if form.fields['questions'].queryset.count() == 0:
                    messages.warning(request, "No questions found for this topic. Please select another topic.")

        context = {
            'quiz': quiz,
            'form': form,
            'title': f'Bulk add questions to {quiz.title}',
            'opts': self.model._meta,
        }
        return render(request, 'admin/public_quiz/bulk_add_questions.html', context)

    def display_quiz_link(self, obj):
        if obj.pk:
            url = reverse('public_quiz:info', kwargs={'slug': obj.slug})
            return format_html(
                '<a href="{}" target="_blank" style="background: #28a745; color: white; padding: 2px 8px; border-radius: 3px; text-decoration: none;">🔗 Open</a>',
                url
            )
        return "N/A"
    display_quiz_link.short_description = "Link"

    def question_count(self, obj):
        return obj.quiz_questions.count()
    question_count.short_description = "Questions"

    def attempt_count(self, obj):
        return obj.attempts.filter(completed_at__isnull=False).count()
    attempt_count.short_description = "Attempts"

    def export_quiz_attempts(self, request, queryset):
        """Export quiz attempts as CSV with error handling"""
        if not queryset:
            messages.warning(request, "No quizzes selected.")
            return

        try:
            response = HttpResponse(content_type='text/csv')
            filename = f"quiz_attempts_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            response['Content-Disposition'] = f'attachment; filename="{filename}"'

            writer = csv.writer(response)
            writer.writerow(['Quiz Title', 'Topic', 'Name', 'Email', 'Mobile', 'Score', 'Correct', 'Wrong', 'Skipped', 'Completed Date'])

            for quiz in queryset:
                # Safely get topic name (Topic model likely uses 'title')
                topic_name = 'No Topic'
                if quiz.topic:
                    if hasattr(quiz.topic, 'title'):
                        topic_name = str(quiz.topic.title)
                    elif hasattr(quiz.topic, 'name'):
                        topic_name = str(quiz.topic.name)
                    else:
                        topic_name = str(quiz.topic)

                attempts = PublicAttempt.objects.filter(
                    quiz=quiz,
                    completed_at__isnull=False
                ).order_by('-score')

                for attempt in attempts:
                    total = attempt.total_questions or 0
                    correct = attempt.correct_answers or 0
                    wrong = attempt.wrong_answers or 0
                    skipped = total - (correct + wrong)
                    score = attempt.score or 0.0

                    writer.writerow([
                        str(quiz.title),
                        topic_name,
                        str(attempt.name),
                        str(attempt.email),
                        str(attempt.mobile),
                        f"{score:.2f}",
                        str(correct),
                        str(wrong),
                        str(skipped),
                        attempt.completed_at.strftime("%Y-%m-%d %H:%M") if attempt.completed_at else ''
                    ])

            messages.success(request, f"Exported {queryset.count()} quizzes.")
            return response
        except Exception as e:
            import traceback
            traceback.print_exc()
            messages.error(request, f"Export failed: {str(e)}")
            return
    export_quiz_attempts.short_description = "Export quiz attempts as CSV"