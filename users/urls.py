from django.urls import path

from mailing.views import verify_email
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('verify/<uuid:token>/', verify_email, name='verify_email'),
]
