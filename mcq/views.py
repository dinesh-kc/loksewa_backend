# mcq/views.py
from django.shortcuts import render, get_object_or_404, redirect
from .models import Question, QuizAttempt, Answer, Choice,Bookmark,SpacedRevision
from courses.models import *
from django.utils import timezone
from datetime import timedelta
from enrollments.models import Enrollment



from django.db.models import Prefetch
from courses.models import Course




from django.http import JsonResponse
from django.views.decorators.http import require_POST


from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
# from .models import Question, Bookmark
# from enrollment.models import Enrollment



def check_mcq_limit(user):
    # आज कतिपटक MCQ खेलियो भनेर गन्ने
    today = timezone.now().date()
    attempts_today = QuizAttempt.objects.filter(user=user, started_at__date=today).count()
    
    if attempts_today >= 5:
        return False # लिमिट सकियो
    return True

def start_quiz(request, topic_id):
    topic = get_object_or_404(Topic, id=topic_id)
    # '?' ले प्रश्नहरूलाई Randomly अर्डर गर्छ
    course = topic.unit.subject.course

    # यदि कोर्स फ्री छैन र प्रयोगकर्ता प्रिमियम छैन भने लिमिट चेक गर्ने
    is_premium = Enrollment.objects.filter(user=request.user, course=course, is_trial=False).exists()
    
    if not course.is_free and not is_premium:
        if not check_mcq_limit(request.user):
            return render(request, 'enrollments/pay_prompt.html', {
                'message': "तपाईंको आजको ५ वटा निःशुल्क MCQ को कोटा सकियो। थप अभ्यास गर्न कृपया कोर्स खरिद गर्नुहोस्।"
            })

    questions = Question.objects.filter(topic=topic, is_active=True).order_by('?')[:10]

    if request.method == "POST":
        attempt = QuizAttempt.objects.create(
            user=request.user, 
            topic=topic, 
            total_questions=len(questions)
        )
        
        score = 0
        for question in questions:
            choice_id = request.POST.get(f'question_{question.id}')
            if choice_id:
                selected_choice = Choice.objects.get(id=choice_id)
                is_correct = selected_choice.is_correct
                
                Answer.objects.create(
                    attempt=attempt,
                    question=question,
                    selected_choice=selected_choice,
                    is_correct=is_correct
                )
                
                if is_correct:
                    score += question.marks
                else:
                    score -= question.negative_marks

        attempt.score = score
        attempt.complete_quiz()
        return redirect('quiz_result', attempt_id=attempt.id)

    return render(request, 'mcq/take_quiz.html', {'questions': questions, 'topic': topic})


def quiz_result(request, attempt_id):
    attempt = get_object_or_404(QuizAttempt, id=attempt_id)
    return render(request, 'mcq/result.html', {'attempt': attempt})

from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.utils import timezone
from django.db.models import Prefetch

@login_required
def topic_detail(request, topic_id):
    topic = get_object_or_404(Topic, id=topic_id)
    user = request.user
    course = topic.unit.subject.course

    # 1. Access Control
    enrollment = Enrollment.objects.filter(
        user=user,
        course=course,
        is_active=True
    ).first()

    if not enrollment:
        return render(request, 'courses/access_denied.html', {'topic': topic})

    # 2. Daily Limit (Trial users only)
    if enrollment.is_trial:
        today = timezone.now().date()
        daily_attempts = QuizAttempt.objects.filter(
            user=user,
            topic=topic,
            started_at__date=today
        ).count()

        if daily_attempts >= 5:
            return render(request, 'mcq/daily_limit.html')

    # 3. Stable Question Query (important for pagination)
    question_list = Question.objects.filter(
        topic=topic,
        is_active=True
    ).order_by('id').prefetch_related('choices')

    paginator = Paginator(question_list, 5)
    page_number = request.GET.get('page')
    questions = paginator.get_page(page_number)

    # 4. User Bookmarks (fast lookup)
    user_bookmarks = set(
        Bookmark.objects.filter(user=user)
        .values_list('question_id', flat=True)
    )

    context = {
        'topic': topic,
        'questions': questions,
        'user_bookmarks': user_bookmarks
    }

    return render(request, 'mcq/topic_detail.html', context)

@require_POST
@login_required
def toggle_bookmark(request, question_id):
    question = get_object_or_404(Question, id=question_id)

    bookmark, created = Bookmark.objects.get_or_create(
        user=request.user,
        question=question
    )

    if created:
        return JsonResponse({'status': 'added'})
    else:
        bookmark.delete()
        return JsonResponse({'status': 'removed'})

def daily_limit_reached(request):
    return render(request, 'mcq/daily_limit.html')




import random
from django.db.models import F
from analytics.models import TopicProgress, UserStats

def quiz_mode(request, topic_id):
    topic = get_object_or_404(Topic, id=topic_id)
    # Database bata real questions line
    all_questions = list(Question.objects.filter(topic=topic).prefetch_related('choices'))
    
    # 50 questions randomly line
    sample_size = min(len(all_questions), 50)
    questions = random.sample(all_questions, sample_size)

    if request.method == 'POST':
        correct = 0
        wrong = 0
        
        for q in questions:
            user_choice_id = request.POST.get(f'q_{q.id}')
            correct_choice = next((c for c in q.choices.all() if c.is_correct), None)
            
            if user_choice_id:
                if str(user_choice_id) == str(correct_choice.id):
                    correct += 1
                    q.is_correct_in_quiz = True # Mark for result template
                else:
                    wrong += 1
                    q.is_correct_in_quiz = False
            else:
                q.is_correct_in_quiz = False # Unattempted is wrong for marking but not negative
        
        # Calculation
        score = (correct * 1) - (wrong * 0.25)
        unattempted = len(questions) - (correct + wrong)

        # Update Analytics
        progress, _ = TopicProgress.objects.get_or_create(user=request.user, topic=topic)
        progress.total_attempted += (correct + wrong)
        progress.correct_count += correct
        progress.update_accuracy()

        stats, _ = UserStats.objects.get_or_create(user=request.user)
        stats.total_score += float(score)
        stats.total_quizzes += 1
        stats.save()

        return render(request, 'mcq/quiz_result.html', {
            'topic': topic,
            'questions': questions,
            'score': score,
            'correct': correct,
            'wrong': wrong,
            'unattempted': unattempted
        })

    return render(request, 'mcq/quiz_mode.html', {'topic': topic, 'questions': questions})


def bookmark_list(request):
    # User ke saare bookmarked question IDs nikalna
    user_bookmarks = Bookmark.objects.filter(user=request.user).select_related('question__topic__unit__subject__course')
    # print(user_bookmarks)
    # print("user bookmarks")
    # Courses ko filter karna jinka questions bookmark hain
    courses = Course.objects.filter(
        subject__unit__topic__question__bookmark__user=request.user
    ).distinct()
    print(courses)

    return render(request, 'mcq/bookmark_courses.html', {
        'courses': courses,
    })

# views.py
def course_bookmarks(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    
    # User le bookmark gareka questions matra line
    questions_list = Question.objects.filter(
        topic__unit__subject__course=course,
        bookmark__user=request.user
    ).prefetch_related('choices', 'topic').distinct()

    mode = request.GET.get('mode', 'study')
    
    # 1. QUIZ MODE & POST HANDLING
    if mode == 'quiz' or request.method == 'POST':
        # Shuffle garne logic
        questions = list(questions_list)
        random.seed(42) # Consistent result summary ko lagi
        random.shuffle(questions)
        questions = questions[:50]

        if request.method == 'POST':
            correct = 0
            wrong = 0
            
            for q in questions:
                user_choice_id = request.POST.get(f'q_{q.id}')
                # Real correct answer database bata nikalne
                correct_choice = q.choices.filter(is_correct=True).first()
                is_correct = str(user_choice_id) == str(correct_choice.id) if user_choice_id else False
                # Spaced Repetition logic trigger
                update_spaced_repetition(request.user, q, is_correct)
                if user_choice_id:
                    if str(user_choice_id) == str(correct_choice.id):
                        correct += 1
                        q.is_correct_in_quiz = True
                    else:
                        wrong += 1
                        q.is_correct_in_quiz = False
                else:
                    q.is_correct_in_quiz = False

            # Negative Marking (1 mark for correct, -0.25 for wrong)
            score = (correct * 1) - (wrong * 0.25)
            unattempted = len(questions) - (correct + wrong)

            # Analytics update (Optional: Bookmark quiz ko data pani track garne bhaye)
            stats, _ = UserStats.objects.get_or_create(user=request.user)
            stats.total_score += float(score)
            stats.total_quizzes += 1
            stats.save()

            # Direct result template render garne
            return render(request, 'mcq/quiz_result.html', {
                'course': course,        # Yo thapnu hos
                'topic': {'title': f'Result: {course.title} (Bookmarks)'}, # topic.id yaha chaina
                'questions': questions,
                'score': score,
                'correct': correct,
                'wrong': wrong,
                'unattempted': unattempted
            })
        # GET request ma Quiz page dekhine
        return render(request, 'mcq/quiz_mode.html', {
            'topic': {'title': f'Bookmark Quiz: {course.title}'},
            'questions': questions
        })

    # 2. STUDY MODE
    user_bookmarks = list(questions_list.values_list('id', flat=True))
    return render(request, 'mcq/bookmark_questions.html', {
        'course': course,
        'questions': questions_list,
        'user_bookmarks': user_bookmarks
    })

def update_spaced_repetition(user, question, is_correct):
    revision, created = SpacedRevision.objects.get_or_create(user=user, question=question)
    
    if is_correct:
        # Yadi milayo bhane interval badhaune (e.g., 1 -> 3 -> 7 -> 15 days)
        if revision.interval == 1:
            revision.interval = 3
        elif revision.interval == 3:
            revision.interval = 7
        else:
            revision.interval *= 2 # Double the interval
            
        if revision.interval > 30: # 30 din bhanda mathi gayo bhane mastered manne
            revision.is_mastered = True
    else:
        # Yadi bigaryo bhane interval reset garera bholi ko date rakhne
        revision.interval = 1
        revision.is_mastered = False
    
    revision.next_review = timezone.now() + timedelta(days=revision.interval)
    revision.save()

def daily_revision_quiz(request):
    # Aaja review garnu parne questions matra filter garne
    now = timezone.now()
    revisions = SpacedRevision.objects.filter(
        user=request.user, 
        next_review__lte=now,
        is_mastered=False
    ).select_related('question')
    
    questions = [r.question for r in revisions]
    
    if not questions:
        return render(request, 'mcq/revision_empty.html') # Sabai review sakiyo bhane

    return render(request, 'mcq/quiz_mode.html', {
        'topic': {'title': 'Daily Smart Revision'},
        'questions': questions,
        'is_revision': True
    })

# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework.permissions import IsAuthenticated
# from django.utils import timezone

# from .models import Question, Choice, QuizAttempt, Answer
# from courses.models import Topic
# from analytics.models import TopicProgress, UserStats


# class SubmitQuizView(APIView):
#     permission_classes = [IsAuthenticated]

#     def post(self, request):

#         topic_id = request.data.get("topic_id")
#         answers = request.data.get("answers")  
#         # answers format:
#         # [
#         #   {"question_id": 1, "choice_id": 4},
#         #   {"question_id": 2, "choice_id": 7}
#         # ]

#         try:
#             topic = Topic.objects.get(id=topic_id)
#         except Topic.DoesNotExist:
#             return Response({"error": "Invalid topic"}, status=400)

#         total_questions = len(answers)
#         score = 0
#         correct_count = 0

#         # Create QuizAttempt
#         attempt = QuizAttempt.objects.create(
#             user=request.user,
#             topic=topic,
#             total_questions=total_questions,
#             started_at=timezone.now()
#         )

#         for item in answers:
#             question_id = item.get("question_id")
#             choice_id = item.get("choice_id")

#             try:
#                 question = Question.objects.get(id=question_id)
#                 selected_choice = Choice.objects.get(id=choice_id)
#             except:
#                 continue

#             is_correct = selected_choice.is_correct

#             if is_correct:
#                 score += question.marks
#                 correct_count += 1
#             else:
#                 score -= question.negative_marks

#             # Save Answer
#             Answer.objects.create(
#                 attempt=attempt,
#                 question=question,
#                 selected_choice=selected_choice,
#                 is_correct=is_correct
#             )

#         # Update attempt
#         attempt.score = score
#         attempt.completed_at = timezone.now()
#         attempt.save()

#         # ===============================
#         # 🔥 UPDATE TOPIC PROGRESS HERE
#         # ===============================

#         progress, created = TopicProgress.objects.get_or_create(
#             user=request.user,
#             topic=topic
#         )

#         progress.total_attempted += total_questions
#         progress.correct_count += correct_count
#         progress.update_accuracy()

#         # ===============================
#         # 🔥 UPDATE USER STATS (Leaderboard)
#         # ===============================

#         stats, created = UserStats.objects.get_or_create(user=request.user)
#         stats.total_score += score
#         stats.total_quizzes += 1
#         stats.save()

#         return Response({
#             "message": "Quiz submitted successfully",
#             "score": score,
#             "correct_answers": correct_count,
#             "total_questions": total_questions,
#             "accuracy": progress.accuracy
#         })