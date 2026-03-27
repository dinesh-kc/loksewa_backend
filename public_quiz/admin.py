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
    topic = forms.ModelChoiceField(
        queryset=Topic.objects.all(), 
        required=True, 
        label="Select Topic",
        widget=forms.Select(attrs={
            'class': 'topic-select',
        })
    )
    
    difficulty = forms.MultipleChoiceField(
        choices=Question.DIFFICULTY,
        required=False,
        label="Filter by Difficulty",
        help_text="Leave empty to select all difficulties",
        widget=forms.CheckboxSelectMultiple
    )
    
    questions = forms.ModelMultipleChoiceField(
        queryset=Question.objects.none(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="Select Questions"
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Initialize with empty queryset
        self.fields['questions'].queryset = Question.objects.none()
        
        # If POST data exists, use it to filter questions
        if self.data:
            topic_id = self.data.get('topic')
            difficulty = self.data.getlist('difficulty')
            
            if topic_id:
                try:
                    topic_id = int(topic_id)
                    queryset = Question.objects.filter(topic_id=topic_id, is_active=True)
                    
                    # Apply difficulty filter if selected
                    if difficulty:
                        queryset = queryset.filter(difficulty__in=difficulty)
                    
                    # Order by ID for better display
                    self.fields['questions'].queryset = queryset.order_by('id')
                        
                except (ValueError, TypeError):
                    pass

@admin.register(PublicQuiz)
class PublicQuizAdmin(admin.ModelAdmin):
    list_display = ['display_title', 'topic', 'is_active', 'question_count', 'attempt_count', 'created_at', 'display_quiz_link']
    list_filter = ['is_active', 'topic', 'created_at']
    search_fields = ('title', 'topic__name', 'topic__title')
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
    
    def display_title(self, obj):
        return format_html('<strong>{}</strong>', obj.title)
    display_title.short_description = 'Quiz Title'
    display_title.admin_order_field = 'title'

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
        
        # Initialize variables
        topic_id = None
        selected_difficulties = []
        
        if request.method == 'POST':
            # Check if this is an add action or filter action
            is_add_action = 'add_questions' in request.POST
            
            form = BulkAddQuestionForm(request.POST)
            
            # Populate questions queryset based on POST data
            topic_id = request.POST.get('topic')
            selected_difficulties = request.POST.getlist('difficulty')
            
            if topic_id:
                try:
                    queryset = Question.objects.filter(topic_id=topic_id, is_active=True)
                    if selected_difficulties:
                        queryset = queryset.filter(difficulty__in=selected_difficulties)
                    form.fields['questions'].queryset = queryset.order_by('id')
                except (ValueError, TypeError):
                    pass
            
            if is_add_action:
                # This is the actual submission to add questions
                if form.is_valid():
                    questions = form.cleaned_data['questions']
                    
                    if not questions:
                        messages.warning(request, "No questions selected. Please select at least one question.")
                    else:
                        # Get existing questions to avoid duplicates
                        existing_ids = set(PublicQuizQuestion.objects.filter(
                            quiz=quiz
                        ).values_list('question_id', flat=True))
                        
                        # Get current max order
                        max_order = PublicQuizQuestion.objects.filter(
                            quiz=quiz
                        ).aggregate(Max('order'))['order__max'] or 0
                        
                        added = 0
                        skipped = 0
                        
                        for q in questions:
                            if q.id not in existing_ids:
                                max_order += 1
                                PublicQuizQuestion.objects.create(
                                    quiz=quiz, 
                                    question=q, 
                                    order=max_order
                                )
                                added += 1
                            else:
                                skipped += 1
                        
                        # Show success message
                        msg = f"Successfully added {added} questions to '{quiz.title}'."
                        if skipped > 0:
                            msg += f" Skipped {skipped} duplicate question(s)."
                        
                        messages.success(request, msg)
                        
                    return HttpResponseRedirect(
                        reverse('admin:public_quiz_publicquiz_change', args=[quiz.id])
                    )
                else:
                    # Form is invalid, show errors
                    for field, errors in form.errors.items():
                        for error in errors:
                            messages.error(request, f"{field}: {error}")
            else:
                # This is just filtering (apply filters)
                # Show info message about filtered results
                if topic_id:
                    count = form.fields['questions'].queryset.count()
                    if count > 0:
                        messages.info(request, f"Found {count} question(s) matching your criteria.")
                    else:
                        messages.warning(request, f"No questions found for the selected topic and difficulty filters.")
        else:
            # GET request - initial form
            topic_id = request.GET.get('topic')
            selected_difficulties = request.GET.getlist('difficulty')
            
            if topic_id:
                # Create form with GET data
                form = BulkAddQuestionForm(request.GET)
                try:
                    queryset = Question.objects.filter(topic_id=topic_id, is_active=True)
                    if selected_difficulties:
                        queryset = queryset.filter(difficulty__in=selected_difficulties)
                    form.fields['questions'].queryset = queryset.order_by('id')
                except (ValueError, TypeError):
                    form = BulkAddQuestionForm()
            else:
                form = BulkAddQuestionForm()
        
        # Prepare context for template
        context = {
            'quiz': quiz,
            'form': form,
            'title': f'Bulk add questions to {quiz.title}',
            'opts': self.model._meta,
            'total_questions': 0,
            'filtered_count': 0,
        }
        
        # Calculate counts for display
        if topic_id:
            try:
                all_questions = Question.objects.filter(topic_id=topic_id, is_active=True)
                filtered_questions = all_questions
                
                if selected_difficulties:
                    filtered_questions = all_questions.filter(difficulty__in=selected_difficulties)
                
                context['total_questions'] = all_questions.count()
                context['filtered_count'] = filtered_questions.count()
            except (ValueError, TypeError):
                pass
        
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
            writer.writerow(['Quiz Title', 'Quiz ID', 'Topic', 'Name', 'Email', 'Mobile', 'Score', 'Correct', 'Wrong', 'Skipped', 'Completed Date'])

            for quiz in queryset:
                # Safely get topic name
                topic_name = 'No Topic'
                if quiz.topic:
                    if hasattr(quiz.topic, 'name'):
                        topic_name = str(quiz.topic.name)
                    elif hasattr(quiz.topic, 'title'):
                        topic_name = str(quiz.topic.title)
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
                        str(quiz.id),
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