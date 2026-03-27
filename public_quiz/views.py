# public_quiz/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.utils import timezone
from django.http import HttpResponse
from django.template.loader import get_template
from django.template import TemplateDoesNotExist
import traceback

# Import models - use absolute import to be safe
from public_quiz.models import PublicQuiz, PublicQuizQuestion, PublicAttempt, PublicAnswer
from mcq.models import Choice

# -------------------------
# Public Quiz Landing Page + Info Form
# -------------------------
# -------------------------
# Public Quiz Landing Page + Info Form
# -------------------------
def public_quiz_info(request, slug):
    try:
        print(f"\n{'='*50}")
        print(f"PUBLIC QUIZ INFO VIEW - START")
        print(f"Slug: {slug}")
        print(f"Request method: {request.method}")
        print(f"Session key: {request.session.session_key}")
        print(f"{'='*50}\n")
        
        # Step 1: Try to get the quiz
        try:
            quiz = PublicQuiz.objects.get(slug=slug, is_active=True)
            print(f"✓ Quiz found: {quiz.title} (ID: {quiz.id})")
        except PublicQuiz.DoesNotExist:
            print(f"✗ Quiz with slug '{slug}' not found or not active")
            return HttpResponse(f"Quiz with slug '{slug}' not found or not active", status=404)
        
        # Step 2: Count questions
        try:
            total_questions = PublicQuizQuestion.objects.filter(quiz=quiz).count()
            print(f"✓ Total questions in quiz: {total_questions}")
        except Exception as e:
            print(f"✗ Error counting questions: {str(e)}")
            total_questions = 0
        
        # Step 3: Handle POST request
        if request.method == "POST":
            print("\n--- Processing POST request ---")
            print(f"POST data: {request.POST}")
            
            name = request.POST.get("name")
            email = request.POST.get("email")
            mobile = request.POST.get("mobile")
            
            print(f"Name: {name}, Email: {email}, Mobile: {mobile}")

            # Validate form data
            if not all([name, email, mobile]):
                print("✗ Validation failed: missing fields")
                messages.error(request, "All fields are required!")
                return redirect(request.path)
            
            # Check if quiz has questions
            if total_questions == 0:
                print("✗ Validation failed: no questions in quiz")
                messages.error(request, "This quiz has no questions yet!")
                return redirect('public_quiz:info', slug=slug)

            # Create new attempt
            try:
                # Get or create session
                if not request.session.session_key:
                    request.session.create()
                    print(f"✓ New session created: {request.session.session_key}")
                
                attempt = PublicAttempt.objects.create(
                    quiz=quiz,
                    name=name,
                    email=email,
                    mobile=mobile,
                    total_questions=total_questions,
                    session_key=request.session.session_key
                )
                print(f"✓ Attempt created with ID: {attempt.id}")
                
                # Store attempt ID in session
                request.session['public_attempt_id'] = attempt.id
                request.session['public_quiz_slug'] = slug
                request.session.modified = True
                print(f"✓ Session updated with attempt_id: {attempt.id}")
                
                # Check if quiz has scheduled start time
                if quiz.start_time and timezone.now() < quiz.start_time:
                    # Quiz hasn't started yet, go to waiting page
                    print(f"✓ Quiz starts at {quiz.start_time}, redirecting to waiting page")
                    return redirect('public_quiz:waiting', slug=slug)
                else:
                    # Quiz can start now
                    print(f"✓ Quiz can start now, redirecting to take page")
                    return redirect('public_quiz:take', slug=slug)
                
            except Exception as e:
                print(f"✗ Error creating attempt: {str(e)}")
                traceback.print_exc()
                messages.error(request, f"Error creating attempt: {str(e)}")
                return redirect(request.path)

        # Step 4: GET request - show the form
        print("\n--- Rendering template for GET request ---")
        
        # Check if template exists
        try:
            get_template('public_quiz/public_quiz_info.html')
            print("✓ Template found: public_quiz/public_quiz_info.html")
            template_name = 'public_quiz/public_quiz_info.html'
        except TemplateDoesNotExist:
            try:
                get_template('public_quiz_info.html')
                print("✓ Template found: public_quiz_info.html")
                template_name = 'public_quiz_info.html'
            except TemplateDoesNotExist:
                print("✗ Template not found!")
                return HttpResponse("Template not found. Check template location.", status=500)
        
        context = {
            "quiz": quiz,
            "total_questions": total_questions,
            "current_time": timezone.now(),
            "start_time": quiz.start_time,
            "end_time": quiz.end_time,
        }
        print(f"Context prepared: {context}")
        
        return render(request, template_name, context)
        
    except Exception as e:
        print("\n" + "="*50)
        print("UNHANDLED EXCEPTION in public_quiz_info:")
        print(f"Error type: {type(e).__name__}")
        print(f"Error message: {str(e)}")
        print("Traceback:")
        traceback.print_exc()
        print("="*50 + "\n")
        
        return HttpResponse(f"""
            <h1>Error in Quiz Info View</h1>
            <p><strong>Error type:</strong> {type(e).__name__}</p>
            <p><strong>Error message:</strong> {str(e)}</p>
            <h3>Debug Info:</h3>
            <ul>
                <li>Slug: {slug}</li>
                <li>Method: {request.method}</li>
                <li>Session key: {request.session.session_key}</li>
            </ul>
            <h3>Traceback:</h3>
            <pre>{traceback.format_exc()}</pre>
        """)
# -------------------------
# Take Quiz
# -------------------------
# Add this to the public_quiz_take function

def public_quiz_take(request, slug):
    """
    Step 2: User takes the quiz with timer
    """
    try:
        quiz = get_object_or_404(PublicQuiz, slug=slug, is_active=True)
        
        # Check if quiz has a scheduled start time
        if quiz.start_time and timezone.now() < quiz.start_time:
            return redirect('public_quiz:waiting', slug=slug)
        
        # Check if quiz has ended based on scheduled end time
        if quiz.end_time and timezone.now() > quiz.end_time:
            messages.warning(request, f"This quiz ended on {quiz.end_time.strftime('%B %d, %Y at %I:%M %p')}")
            return redirect('public_quiz:info', slug=slug)
        
        # Get attempt from session
        attempt_id = request.session.get('public_attempt_id')
        if not attempt_id:
            messages.warning(request, "Please fill your information first!")
            return redirect('public_quiz:info', slug=slug)
        
        attempt = get_object_or_404(PublicAttempt, id=attempt_id, quiz=quiz)
        
        # Check if quiz is already completed
        if attempt.completed_at:
            messages.info(request, "You've already completed this quiz!")
            return redirect('public_quiz:result', slug=slug)
        
        # Get all questions
        quiz_questions = PublicQuizQuestion.objects.filter(quiz=quiz).select_related('question')
        questions = [qq.question for qq in quiz_questions]
        
        # Set start time if first visit
        if not attempt.started_at:
            attempt.started_at = timezone.now()
            attempt.save()
        
        # --- Determine actual end time (whichever is earlier: time-limit end OR scheduled end) ---
        now = timezone.now()
        
        # End time based on time limit (if set)
        time_limit_end = None
        if quiz.time_limit and quiz.time_limit > 0:
            time_limit_end = attempt.started_at + timezone.timedelta(minutes=quiz.time_limit)
        
        # Scheduled end time (if set)
        scheduled_end = quiz.end_time
        
        # Choose the earliest valid end time
        end_times = []
        if time_limit_end:
            end_times.append(time_limit_end)
        if scheduled_end:
            end_times.append(scheduled_end)
        
        if end_times:
            quiz_end_time = min(end_times)
        else:
            # Fallback: 30 minutes (should not happen as time_limit is required, but just in case)
            quiz_end_time = attempt.started_at + timezone.timedelta(minutes=30)
        
        # Calculate remaining seconds
        if now >= quiz_end_time:
            remaining_seconds = 0
        else:
            remaining_seconds = (quiz_end_time - now).total_seconds()
        
        # If time is up, auto-submit
        if remaining_seconds <= 0:
            messages.warning(request, "Time's up! Your quiz has been auto-submitted.")
            return auto_submit_quiz(request, attempt, questions)
        
        # Handle POST (answer submission)
        if request.method == "POST":
            correct_count = 0
            wrong_count = 0
            
            for question in questions:
                choice_id = request.POST.get(f'q_{question.id}')
                
                if choice_id:
                    try:
                        selected_choice = Choice.objects.get(id=choice_id, question=question)
                        is_correct = selected_choice.is_correct
                        
                        PublicAnswer.objects.create(
                            attempt=attempt,
                            question=question,
                            selected_choice=selected_choice,
                            is_correct=is_correct
                        )
                        
                        if is_correct:
                            correct_count += 1
                        else:
                            wrong_count += 1
                    except Choice.DoesNotExist:
                        wrong_count += 1
                else:
                    wrong_count += 1

            # Calculate score (1 for correct, -0.25 for wrong)
            score = (correct_count * 1) - (wrong_count * 0.25)
            
            attempt.score = max(0, score)
            attempt.correct_answers = correct_count
            attempt.wrong_answers = wrong_count
            attempt.completed_at = timezone.now()
            attempt.save()
            
            return redirect('public_quiz:result', slug=slug)
        
        # GET request: render quiz page
        return render(request, 'public_quiz/public_quiz_take.html', {
            'quiz': quiz,
            'questions': questions,
            'total_questions': len(questions),
            'attempt': attempt,
            'time_limit_minutes': quiz.time_limit,
            'remaining_seconds': int(remaining_seconds),
            'start_time': attempt.started_at.timestamp(),
            'end_time_display': quiz_end_time.strftime('%Y-%m-%d %H:%M:%S'),  # optional
        })
        
    except Exception as e:
        print("="*50)
        print("ERROR in public_quiz_take:")
        print(f"Error type: {type(e).__name__}")
        print(f"Error message: {str(e)}")
        traceback.print_exc()
        print("="*50)
        return HttpResponse(f"Error in quiz take view: {str(e)}", status=500)
    
def auto_submit_quiz(request, attempt, questions):
    """Auto-submit quiz when time runs out"""
    correct_count = 0
    wrong_count = 0
    
    # Get existing answers (if any)
    existing_answers = PublicAnswer.objects.filter(attempt=attempt)
    answered_question_ids = set(ans.question_id for ans in existing_answers)
    
    for question in questions:
        if question.id not in answered_question_ids:
            # Question not answered, count as wrong
            wrong_count += 1
    
    # Count correct/wrong from existing answers
    for answer in existing_answers:
        if answer.is_correct:
            correct_count += 1
        else:
            wrong_count += 1
    
    # Calculate score
    score = (correct_count * 1) - (wrong_count * 0.25)
    
    # Update attempt
    attempt.score = max(0, score)
    attempt.correct_answers = correct_count
    attempt.wrong_answers = wrong_count
    attempt.completed_at = timezone.now()
    attempt.save()
    
    return redirect('public_quiz:result', slug=attempt.quiz.slug)
# -------------------------
# Quiz Result
# # -------------------------

# public_quiz/views.py

def public_quiz_result(request, slug):
    """
    Step 3: Show promotional page instead of actual results
    """
    try:
        quiz = get_object_or_404(PublicQuiz, slug=slug)
        
        # Get attempt from session
        attempt_id = request.session.get('public_attempt_id')
        if not attempt_id:
            messages.error(request, "No quiz attempt found!")
            return redirect('public_quiz:info', slug=slug)
        
        attempt = get_object_or_404(PublicAttempt, id=attempt_id, quiz=quiz)
        
        # We still calculate but don't show to user
        # This data will be used for admin exports only
        
        # Get leaderboard (but don't show actual scores)
        leaderboard = PublicAttempt.objects.filter(
            quiz=quiz, 
            completed_at__isnull=False
        ).order_by('-score', 'completed_at')[:10]
        
        return render(request, 'public_quiz/public_quiz_result.html', {
            'quiz': quiz,
            'attempt': attempt,
            'leaderboard': leaderboard,  # Will show only names, not scores
            'facebook_page': 'GKLaboratory',  # Your Facebook page name
            'facebook_url': 'https://www.facebook.com/people/GK-Laboratory/100090362160712/',  # Update this
        })
        
    except Exception as e:
        print(f"Error in result view: {str(e)}")
        return HttpResponse(f"Error: {str(e)}", status=500)
    
def public_quiz_waiting(request, slug):
    """
    Waiting page for scheduled quizzes
    Shows countdown to quiz start time
    """
    quiz = get_object_or_404(PublicQuiz, slug=slug, is_active=True)
    
    # Get attempt from session
    attempt_id = request.session.get('public_attempt_id')
    if not attempt_id:
        messages.warning(request, "Please fill your information first!")
        return redirect('public_quiz:info', slug=slug)
    
    attempt = get_object_or_404(PublicAttempt, id=attempt_id, quiz=quiz)
    
    # Check if quiz is already completed
    if attempt.completed_at:
        messages.info(request, "You've already completed this quiz!")
        return redirect('public_quiz:result', slug=slug)
    
    # Check if quiz has already started
    if not quiz.start_time or timezone.now() >= quiz.start_time:
        # Quiz should start now, redirect to take page
        return redirect('public_quiz:take', slug=slug)
    
    # Calculate time until start
    time_until_start = quiz.start_time - timezone.now()
    seconds_until_start = int(time_until_start.total_seconds())
    
    # Check if end time is set and quiz hasn't expired
    if quiz.end_time and timezone.now() >= quiz.end_time:
        messages.error(request, "This quiz has already ended!")
        return redirect('public_quiz:info', slug=slug)
    
    context = {
        'quiz': quiz,
        'attempt': attempt,
        'seconds_until_start': seconds_until_start,
        'start_time': quiz.start_time,
    }
    return render(request, 'public_quiz/public_quiz_waiting.html', context)

    
# def public_quiz_result(request, slug):
#     """
#     Step 3: Show quiz results and leaderboard
#     """
#     try:
#         quiz = get_object_or_404(PublicQuiz, slug=slug)
        
#         # Get attempt from session
#         attempt_id = request.session.get('public_attempt_id')
#         if not attempt_id:
#             messages.error(request, "No quiz attempt found!")
#             return redirect('public_quiz:info', slug=slug)
        
#         attempt = get_object_or_404(PublicAttempt, id=attempt_id, quiz=quiz)
        
#         # Get user's answers with question details
#         answers = PublicAnswer.objects.filter(attempt=attempt).select_related('question', 'selected_choice')
        
#         # Get leaderboard (top 10 scores)
#         leaderboard = PublicAttempt.objects.filter(
#             quiz=quiz, 
#             completed_at__isnull=False
#         ).exclude(
#             id=attempt.id
#         ).order_by('-score', 'completed_at')[:10]
        
#         # Calculate rank
#         rank = PublicAttempt.objects.filter(
#             quiz=quiz,
#             completed_at__isnull=False,
#             score__gt=attempt.score
#         ).count() + 1
        
#         return render(request, 'public_quiz/public_quiz_result.html', {
#             'quiz': quiz,
#             'attempt': attempt,
#             'answers': answers,
#             'leaderboard': leaderboard,
#             'rank': rank,
#             'percentage': (attempt.correct_answers / attempt.total_questions * 100) if attempt.total_questions > 0 else 0
#         })
        
#     except Exception as e:
#         print("="*50)
#         print("ERROR in public_quiz_result:")
#         print(f"Error type: {type(e).__name__}")
#         print(f"Error message: {str(e)}")
#         print("Traceback:")
#         traceback.print_exc()
#         print("="*50)
        
#         return HttpResponse(f"Error in quiz result view: {str(e)}", status=500)