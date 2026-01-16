from django.urls import path
from .views import ProtectedView

from .views import(
    HomeView,
    RegisterView,
    VerifyEmailView,
    # LoginView,
    JWTLoginView,
    CourseView,
    CourseDetailView,
    StudentView,
    StudentDetailView
)

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('register/', RegisterView.as_view(), name='register'),
    path('verify-email/', VerifyEmailView.as_view(), name='verify-email'),
    # path('login/', LoginView.as_view(), name='login'),
    path('login/', JWTLoginView.as_view(), name='jwt-login'),
    path('protected/', ProtectedView.as_view(), name='protected'),
    path('courses/', CourseView.as_view(), name='courses'),
    path(
        'courses/<int:course_id>/students/',
        StudentView.as_view(),
        name='students'
    ),
    path(
        'students/<int:student_id>/',
        StudentDetailView.as_view(),
        name='student-detail'
    ),
    path(
    'courses/<int:course_id>/',
        CourseDetailView.as_view(),
        name='course-detail'
    ),

]
