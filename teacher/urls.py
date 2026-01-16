from django.urls import path
from django.http import HttpRequest, HttpResponse


urlpatterns = [
    path('', lambda request: HttpResponse("Teacher Home Page"), name='teacher-home'),
]
