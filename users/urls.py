from django.urls import path

from mailing.views import verify_email,SignUpView,CustomLoginView,CustomLogoutView
from . import views

# Маршруты для аутентификации
urlpatterns = [
    path('signup/', SignUpView.as_view(), name='signup'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', CustomLogoutView.as_view(), name='logout'),
    path('verify/<int:user_id>/', verify_email, name='verify_email'),
]
