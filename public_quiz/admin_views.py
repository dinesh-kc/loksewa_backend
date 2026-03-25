# public_quiz/admin_views.py
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.contrib import messages
from django.shortcuts import redirect
import csv
import xlwt
from datetime import datetime
from .models import PublicQuiz, PublicAttempt

@staff_member_required
def export_quiz_results(request):
    quiz_id = request.GET.get('quiz_id')
    format_type = request.GET.get('format', 'csv')  # csv, excel, rank
    
    if not quiz_id:
        messages.error(request, "Quiz ID required")
        return redirect('admin:public_quiz_publicquiz_changelist')
    
    quiz = get_object_or_404(PublicQuiz, id=quiz_id)
    attempts = PublicAttempt.objects.filter(
        quiz=quiz, 
        completed_at__isnull=False
    ).order_by('-score', 'completed_at')
    
    # Rank List Format (Facebook post को लागि)
    if format_type == 'rank':
        return generate_rank_list(request, quiz, attempts)
    
    # Excel Format
    elif format_type == 'excel':
        return generate_excel_file(request, quiz, attempts)
    
    # Default CSV Format
    else:
        return generate_csv_file(request, quiz, attempts)

def generate_csv_file(request, quiz, attempts):
    """Generate CSV file with all details"""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{quiz.title}_results_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Rank', 'Name', 'Email', 'Mobile', 'Score', 'Correct', 'Wrong', 'Skipped', 'Percentage', 'Completed At'])
    
    for idx, attempt in enumerate(attempts, 1):
        skipped = attempt.total_questions - (attempt.correct_answers + attempt.wrong_answers)
        percentage = (attempt.correct_answers / attempt.total_questions * 100) if attempt.total_questions > 0 else 0
        writer.writerow([
            idx,
            attempt.name,
            attempt.email,
            attempt.mobile,
            f"{attempt.score:.2f}",
            attempt.correct_answers,
            attempt.wrong_answers,
            skipped,
            f"{percentage:.1f}%",
            attempt.completed_at.strftime("%Y-%m-%d %H:%M") if attempt.completed_at else ''
        ])
    
    return response

def generate_excel_file(request, quiz, attempts):
    """Generate Excel file with all details and formatting"""
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = f'attachment; filename="{quiz.title}_results_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xls"'
    
    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Results')
    
    # Styles
    header_style = xlwt.easyxf('font: bold on; pattern: pattern solid, fore_colour light_blue; align: horiz center')
    rank_style = xlwt.easyxf('font: bold on; align: horiz center')
    normal_style = xlwt.easyxf('align: horiz left')
    
    # Headers
    headers = ['Rank', 'Name', 'Email', 'Mobile', 'Score', 'Correct', 'Wrong', 'Skipped', 'Percentage', 'Completed At']
    for col, header in enumerate(headers):
        ws.write(0, col, header, header_style)
        ws.col(col).width = 256 * 15  # 15 characters wide
    
    # Data
    for row, attempt in enumerate(attempts, 1):
        skipped = attempt.total_questions - (attempt.correct_answers + attempt.wrong_answers)
        percentage = (attempt.correct_answers / attempt.total_questions * 100) if attempt.total_questions > 0 else 0
        
        ws.write(row, 0, row, rank_style)  # Rank
        ws.write(row, 1, attempt.name, normal_style)
        ws.write(row, 2, attempt.email, normal_style)
        ws.write(row, 3, attempt.mobile, normal_style)
        ws.write(row, 4, f"{attempt.score:.2f}", normal_style)
        ws.write(row, 5, attempt.correct_answers, normal_style)
        ws.write(row, 6, attempt.wrong_answers, normal_style)
        ws.write(row, 7, skipped, normal_style)
        ws.write(row, 8, f"{percentage:.1f}%", normal_style)
        ws.write(row, 9, attempt.completed_at.strftime("%Y-%m-%d %H:%M") if attempt.completed_at else '', normal_style)
    
    wb.save(response)
    return response

def generate_rank_list(request, quiz, attempts):
    """Generate formatted rank list for Facebook post"""
    response = HttpResponse(content_type='text/plain')
    response['Content-Disposition'] = f'attachment; filename="{quiz.title}_rank_list_{datetime.now().strftime("%Y%m%d_%H%M%S")}.txt"'
    
    # Create formatted text for Facebook
    lines = []
    lines.append("=" * 60)
    lines.append(f"🏆 {quiz.title} - RESULT LIST 🏆".center(60))
    lines.append("=" * 60)
    lines.append(f"📅 Date: {datetime.now().strftime('%B %d, %Y')}")
    lines.append(f"📊 Total Participants: {attempts.count()}")
    lines.append("=" * 60)
    lines.append("")
    
    # Add top performers with emojis
    for idx, attempt in enumerate(attempts, 1):
        if idx == 1:
            medal = "🥇 GOLD"
        elif idx == 2:
            medal = "🥈 SILVER"
        elif idx == 3:
            medal = "🥉 BRONZE"
        else:
            medal = f"#{idx}"
        
        percentage = (attempt.correct_answers / attempt.total_questions * 100) if attempt.total_questions > 0 else 0
        
        lines.append(f"{medal} {attempt.name}")
        lines.append(f"   📝 Score: {attempt.score:.2f} | ✅ {attempt.correct_answers} Correct | ❌ {attempt.wrong_answers} Wrong")
        lines.append(f"   📊 Percentage: {percentage:.1f}%")
        lines.append("")
    
    lines.append("=" * 60)
    lines.append("GK Laboratory - Smart MCQ Preparation".center(60))
    lines.append("📱 Follow us for more quizzes!")
    lines.append("=" * 60)
    
    response.write("\n".join(lines))
    return response


def bulk_add_questions_view(self, request, quiz_id):
    quiz = get_object_or_404(PublicQuiz, id=quiz_id)

    if request.method == 'POST':
        form = BulkAddQuestionForm(request.POST)
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
        # Important: pass request.GET to the form so topic selection works
        form = BulkAddQuestionForm(request.GET or None)

    context = {
        'quiz': quiz,
        'form': form,
        'title': f'Bulk add questions to {quiz.title}',
        'opts': self.model._meta,
    }
    return render(request, 'admin/public_quiz/bulk_add_questions.html', context)