from rest_framework import serializers
from django.core.mail import send_mail
from django.conf import settings

from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from rest_framework.exceptions import AuthenticationFailed
from .models import Teacher, EmailVerification, Course, Student
from .utils import generate_verification_code

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = Teacher
        fields = ('username', 'email', 'password')

    def create(self, validated_data):
        user = Teacher.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            is_email_verified=False
        )

        code = generate_verification_code()

        EmailVerification.objects.update_or_create(
            user=user,
            defaults={'code': code}
        )

        send_mail(
            subject='Email tasdiqlash kodi',
            message=f'Sizning tasdiqlash kodingiz: {code}',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False
        )

        return user


class VerifyEmailSerializer(serializers.Serializer):
    email = serializers.EmailField()
    code = serializers.CharField(max_length=6)

    def validate(self, attrs):
        email = attrs.get('email')
        code = attrs.get('code')

        try:
            user = Teacher.objects.get(email=email)
        except Teacher.DoesNotExist:
            raise serializers.ValidationError("Bunday email topilmadi")

        try:
            verification = EmailVerification.objects.get(user=user)
        except EmailVerification.DoesNotExist:
            raise serializers.ValidationError("Tasdiqlash kodi topilmadi")

        if verification.is_expired():
            verification.delete()
            raise serializers.ValidationError("Tasdiqlash kodi eskirgan")

        if verification.code != code:
            raise serializers.ValidationError("Noto‘g‘ri tasdiqlash kodi")

        # hammasi to‘g‘ri bo‘lsa
        user.is_email_verified = True
        user.save()
        verification.delete()

        return attrs

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')

        user = authenticate(username=username, password=password)

        if not user:
            raise AuthenticationFailed("Username yoki parol xato")

        if not user.is_email_verified:
            raise AuthenticationFailed("Email tasdiqlanmagan")

        attrs['user'] = user
        return attrs


class JWTLoginSerializer(LoginSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        user = data['user']

        refresh = RefreshToken.for_user(user)

        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'username': user.username,
            'email': user.email,
        }


class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ['id', 'title', 'description', 'created_at']



class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = [
            'id',
            'full_name',
            'phone_number',
            'backup_phone_number',
            'joined_at'
        ]
