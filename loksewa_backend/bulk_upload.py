import openpyxl
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser

class BulkUploadQuestions(APIView):
    parser_classes = [MultiPartParser]

    def post(self, request):
        file = request.FILES['file']
        wb = openpyxl.load_workbook(file)
        sheet = wb.active

        for row in sheet.iter_rows(min_row=2, values_only=True):
            topic_id, question_text, o1, o2, o3, o4, correct, explanation = row

            question = Question.objects.create(
                topic_id=topic_id,
                question_text=question_text,
                difficulty='MEDIUM',
                explanation=explanation
            )

            options = [o1, o2, o3, o4]

            for index, opt in enumerate(options, start=1):
                Choice.objects.create(
                    question=question,
                    option_text=opt,
                    is_correct=(index == correct)
                )

        return Response({"message": "Questions uploaded successfully"})