# Loksewa MCQ Application – Backend Complete Summary & Frontend Guide

---

# 1. Project Vision

Build a Loksewa MCQ preparation system where:

* Admin creates Courses
* Course → Subjects → Units → Topics
* Topics contain MCQ Questions
* Students enroll in courses (normal or trial)
* Students attempt quizzes topic-wise
* System tracks:

  * Topic progress
  * Quiz attempts
  * Total score
  * Leaderboard ranking

Frontend (GitHub hosted) will consume DRF APIs.
Backend (Django REST Framework) handles authentication, logic, analytics.

---

# 2. Apps Created in Backend

## 1️⃣ courses

Purpose: Manage available courses.

Model: Course
Fields:

* id
* title
* description
* is_trial_available
* trial_days
* price

APIs:
GET /api/courses/
GET /api/courses/{id}/

Response format:
[
{
"id": 1,
"title": "Computer Course",
"description": "Loksewa Computer Preparation",
"is_trial_available": true,
"trial_days": 7,
"price": "1000.00"
}
]

Frontend Use:

* Course listing page
* Course detail page
* Show trial badge
* Show price

---

## 2️⃣ subjects

Purpose: Course structure hierarchy.

Models:

* Subject (belongs to Course)
* Unit (belongs to Subject)
* Topic (belongs to Unit)

APIs:
GET /api/subjects/
GET /api/units/
GET /api/topics/
GET /api/topics/?unit=1

Topic Response:
[
{
"id": 1,
"unit": 1,
"title": "MS Word Basics",
"description": "Introduction"
}
]

Frontend Use:

* Sidebar navigation tree
* Expandable Course → Subject → Unit → Topic layout

---

## 3️⃣ enrollments

Purpose: Control access to courses.

Model: Enrollment
Fields:

* user
* course
* is_trial
* enrolled_at

APIs:
GET /api/enrollments/
POST /api/enrollments/

POST Body:
{
"course": 1,
"is_trial": true
}

Frontend Use:

* Show "My Courses"
* Enable course access only if enrolled
* Show trial countdown badge

---

## 4️⃣ MCQ / Quiz System

Models:

* Question
* Choice
* QuizAttempt

APIs:
GET /api/questions/?topic=1
POST /api/quiz/submit/

Question Response:
[
{
"id": 1,
"topic": 1,
"question_text": "What is CPU?",
"choices": [
{"id": 1, "text": "Central Processing Unit"},
{"id": 2, "text": "Computer Personal Unit"}
]
}
]

Submit Body:
{
"topic_id": 1,
"answers": [
{"question_id": 1, "choice_id": 1}
]
}

Submit Response:
{
"score": 8,
"correct_answers": 4,
"total_questions": 5,
"accuracy": 80
}

Frontend Use:

* Quiz page
* MCQ radio button UI
* Result page
* Accuracy progress bar

---

## 5️⃣ Analytics

Models:

* TopicProgress
* UserStats

APIs:
GET /api/my-progress/
GET /api/leaderboard/

Progress Response:
[
{
"topic": 1,
"total_attempted": 10,
"correct_count": 7,
"accuracy": 70
}
]

Leaderboard Response:
[
{
"username": "student0",
"total_score": 120,
"total_quizzes": 5,
"average_score": 24
}
]

Frontend Use:

* Topic progress bars
* Dashboard analytics
* Ranking page
* Gamification UI

---

# 3. Authentication System

Using JWT (SimpleJWT)

Login API:
POST /api/token/

Body:
{
"username": "student0",
"password": "password123"
}

Response:
{
"refresh": "...",
"access": "..."
}

Frontend must store:

* access token (for API calls)
* optionally refresh token

Header for protected APIs:
Authorization: Bearer <access_token>

---

# 4. Full Backend Flow

1. User logs in → receives token
2. Fetch courses
3. Enroll in course
4. Navigate subjects → units → topics
5. Attempt quiz
6. Submit quiz
7. Backend updates:

   * QuizAttempt
   * TopicProgress
   * UserStats
8. Frontend fetches:

   * My Progress
   * Leaderboard

---

# 5. What We Have Achieved

✔ Course system
✔ Hierarchical structure
✔ Enrollment system
✔ Trial support
✔ MCQ engine
✔ Quiz submission logic
✔ Score calculation
✔ Topic-wise progress tracking
✔ Leaderboard ranking
✔ JWT authentication
✔ Seed test data
✔ REST testing (Talend / VSCode)

Backend is fully functional.

---

# 6. What Is Planned Next (Frontend Perspective)

UI Pages Needed:

1. Login Page : 
 here user can register own . . entire idea is . user can register themself and login . there should be display list of courses . . they can enroll course through purchase ( later we'll integrate khalti api . for now .. just display message please contact admin to this number) . or can run in trial . trial for only 7 days .. but some free courses don't need to extend trial or to purchase . 

 /api/accounts/register/ for register : {
  "username": "ram",
  "email": "ram@gmail.com",
  "password": "password123"
}
POST /api/token/

{
  "username": "ram",
  "password": "password123"
} 


🔐 Authentication

POST /api/accounts/register/

{
  "username": "ram",
  "email": "ram@gmail.com",
  "password": "password123"
}

POST /api/token/

{
  "username": "ram",
  "password": "password123"
}

Returns access + refresh token.

📚 Course Listing

GET /api/courses/

Response:

[
  {
    "id": 1,
    "title": "Computer Course",
    "is_free": false,
    "is_trial_available": true,
    "trial_days": 7,
    "price": "1000.00"
  }
]

Frontend Logic:

if is_free → Show "Start Course"

if trial_available → Show "Start Trial"

else → Show "Purchase"

🎓 Enroll API

POST /api/enrollments/enroll/

Header:

Authorization: Bearer <access_token>

Body:

{
  "course_id": 1
}
2. Course Listing Page
3. My Courses Page
4. Course Detail Page
5. Sidebar Navigation (Subject → Unit → Topic)
6. Quiz Attempt Page
7. Quiz Result Page
8. Dashboard Page
9. Leaderboard Page

State Management Needs:

* Store JWT token
* Store user info
* Store enrolled courses

---

# 7. UI Design Strategy Recommendation

Use this structure:

Dashboard Layout:

* Left Sidebar → Course tree
* Top Navbar → User profile + logout
* Main Content → Dynamic content

Important UI Components:

* Progress bar (topic accuracy)
* Badge (trial / enrolled)
* Timer for quiz (future enhancement)
* Leaderboard table
* Pagination for questions

---

# 8. Backend Is Now Ready For

* React frontend
* Vue frontend
* Next.js
* Plain HTML + JS
* Mobile App (Flutter / React Native)

---

# Final Status

Backend Architecture: Complete & Modular
Authentication: Implemented
Analytics: Implemented
Quiz Engine: Implemented
Testing: Verified

Next Step: Frontend UI Design & API Integration

---

If needed, next we can design:

* API contract document for frontend team
* React folder structure
* UI wireframe plan
* Role-based admin panel design

Backend phase: Successfully completed.
