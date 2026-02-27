import random
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from courses.models import Course, Subject, Unit, Topic
from mcq.models import Question, Choice
from enrollments.models import Enrollment
from analytics.models import TopicProgress, UserStats
from datetime import timedelta


User = get_user_model()


class Command(BaseCommand):
    help = "Seed database with test data"

    def handle(self, *args, **kwargs):

        self.stdout.write("Seeding data...")

        # ======================
        # CREATE USERS
        # ======================

        users = []
        for i in range(5):
            user = User.objects.create_user(
                username=f"student{i}",
                password="password123",
                role="STUDENT"
            )
            users.append(user)

        # ======================
        # CREATE COURSES
        # ======================

        courses = []
        for i in range(6):
            course = Course.objects.create(
                title=f"Computer Course {i}",
                description="Loksewa Computer Preparation",
                is_trial_available=True,
                trial_days=7,
                price=1000,
            )
            courses.append(course)

        # ======================
        # CREATE SUBJECTS, UNITS, TOPICS
        # ======================

        topics_list = []

        for course in courses:
            for s in range(2):
                subject = Subject.objects.create(
                    course=course,
                    title=f"Subject {s} - {course.title}",
                    order=s
                )

                for u in range(2):
                    unit = Unit.objects.create(
                        subject=subject,
                        title=f"Unit {u}",
                        order=u
                    )

                    for t in range(2):
                        topic = Topic.objects.create(
                            unit=unit,
                            title=f"Topic {t}",
                            order=t
                        )
                        topics_list.append(topic)

        # ======================
        # CREATE QUESTIONS
        # ======================

        for topic in topics_list:
            for q in range(3):  # 3 questions per topic
                question = Question.objects.create(
                    topic=topic,
                    question_text=f"What is question {q} for {topic.title}?",
                    difficulty="MEDIUM",
                    marks=1,
                    negative_marks=0.25,
                    explanation="This is explanation."
                )

                correct_option = random.randint(1, 4)

                for c in range(1, 5):
                    Choice.objects.create(
                        question=question,
                        option_text=f"Option {c}",
                        is_correct=(c == correct_option)
                    )

        # ======================
        # ENROLL USERS
        # ======================

        for user in users:
            for course in random.sample(courses, 3):
                Enrollment.objects.create(
                    user=user,
                    course=course,
                    is_trial=True,
                    start_date=timezone.now(),
                    expiry_date=timezone.now() + timedelta(days=7),
                    is_active=True
                )

        # ======================
        # CREATE ANALYTICS DATA
        # ======================

        for user in users:
            stats = UserStats.objects.create(
                user=user,
                total_score=random.randint(50, 200),
                total_quizzes=random.randint(5, 20),
            )

            for topic in random.sample(topics_list, 5):
                attempted = random.randint(5, 20)
                correct = random.randint(1, attempted)

                progress = TopicProgress.objects.create(
                    user=user,
                    topic=topic,
                    total_attempted=attempted,
                    correct_count=correct,
                )
                progress.update_accuracy()

        self.stdout.write(self.style.SUCCESS("Database seeded successfully!"))