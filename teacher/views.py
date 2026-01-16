from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from .models import Course, Student
from .serializers import (
    CourseSerializer,
    StudentSerializer,
    RegisterSerializer, 
    VerifyEmailSerializer,
    #LoginSerializer,
    JWTLoginSerializer
)

class HomeView(APIView):
    def get(self, request):
        return Response(
            {"message": "Teacher panel API ishlayapti 🚀"},
            status=status.HTTP_200_OK
        )


class RegisterView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Ro‘yxatdan o‘tildi. Emailga yuborilgan code ni tasdiqlang."},
                status=status.HTTP_201_CREATED
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class VerifyEmailView(APIView):
    def post(self, request):
        serializer = VerifyEmailSerializer(data=request.data)

        if serializer.is_valid():
            return Response(
                {"message": "Email muvaffaqiyatli tasdiqlandi"},
                status=status.HTTP_200_OK
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# class LoginView(APIView):
    # def post(self, request):
    #     serializer = LoginSerializer(data=request.data)

    #     if serializer.is_valid():
    #         user = serializer.validated_data['user']
    #         return Response(
    #             {
    #                 "message": "Login muvaffaqiyatli",
    #                 "username": user.username,
    #                 "email": user.email,
    #             },
    #             status=status.HTTP_200_OK
    #         )

    #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class JWTLoginView(APIView):
    def post(self, request):
        serializer = JWTLoginSerializer(data=request.data)

        if serializer.is_valid():
            return Response(serializer.validated_data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProtectedView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({
            "message": "Token ishlayapti ✅",
            "user": request.user.username
        })


class CourseView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        courses = Course.objects.filter(teacher=request.user)
        serializer = CourseSerializer(courses, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = CourseSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(teacher=request.user)
        return Response(serializer.data, status=201)

class CourseDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, course_id, user):
        try:
            return Course.objects.get(
                id=course_id,
                teacher=user
            )
        except Course.DoesNotExist:
            return None

    def put(self, request, course_id):
        course = self.get_object(course_id, request.user)
        if not course:
            return Response(
                {"detail": "Course topilmadi"},
                status=404
            )

        serializer = CourseSerializer(
            course,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def delete(self, request, course_id):
        course = self.get_object(course_id, request.user)
        if not course:
            return Response(
                {"detail": "Course topilmadi"},
                status=404
            )

        course.delete()
        return Response(status=204)


class StudentView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, course_id):
        query = request.query_params.get('q')

        students = Student.objects.filter(
            course__id=course_id,
            course__teacher=request.user
        )

        if query:
            students = students.filter(
                Q(full_name__icontains=query) |
                Q(phone_number__icontains=query)
            )

        serializer = StudentSerializer(students, many=True)
        return Response(serializer.data)


    def post(self, request, course_id):
        try:
            course = Course.objects.get(
                id=course_id,
                teacher=request.user
            )
        except Course.DoesNotExist:
            return Response(
                {"detail": "Course topilmadi"},
                status=404
            )

        serializer = StudentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(course=course)
        return Response(serializer.data, status=201)

class StudentDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, student_id, user):
        try:
            return Student.objects.get(
                id=student_id,
                course__teacher=user
            )
        except Student.DoesNotExist:
            return None

    def put(self, request, student_id):
        student = self.get_object(student_id, request.user)
        if not student:
            return Response(
                {"detail": "Student topilmadi"},
                status=404
            )

        serializer = StudentSerializer(
            student,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def delete(self, request, student_id):
        student = self.get_object(student_id, request.user)
        if not student:
            return Response(
                {"detail": "Student topilmadi"},
                status=404
            )

        student.delete()
        return Response(status=204)
