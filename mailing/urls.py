from django.urls import path
from . import views
from .views import (
    SignUpView, CustomLoginView, CustomLogoutView, verify_email
)

# Маршруты для аутентификации
auth_patterns = [
    path('signup/', SignUpView.as_view(), name='signup'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', CustomLogoutView.as_view(), name='logout'),
    path('verify/<int:user_id>/', verify_email, name='verify_email'),
]

# Маршруты для клиентов
client_patterns = [
    path('clients/', views.ClientListView.as_view(), name='client_list'),
    path('clients/<int:pk>/', views.ClientDetailView.as_view(), name='client_detail'),
    path('clients/create/', views.ClientCreateView.as_view(), name='client_create'),
    path('clients/<int:pk>/update/', views.ClientUpdateView.as_view(), name='client_update'),
    path('clients/<int:pk>/delete/', views.ClientDeleteView.as_view(), name='client_delete'),
]

# Маршруты для сообщений
message_patterns = [
    path('messages/', views.MessageListView.as_view(), name='message_list'),
    path('messages/<int:pk>/', views.MessageDetailView.as_view(), name='message_detail'),
    path('messages/create/', views.MessageCreateView.as_view(), name='message_create'),
    path('messages/<int:pk>/update/', views.MessageUpdateView.as_view(), name='message_update'),
    path('messages/<int:pk>/delete/', views.MessageDeleteView.as_view(), name='message_delete'),
]

# Маршруты для рассылок
mailing_patterns = [
    path('mailings/', views.MailingListView.as_view(), name='mailing_list'),
    path('mailings/<int:pk>/', views.MailingDetailView.as_view(), name='mailing_detail'),
    path('mailings/create/', views.MailingCreateView.as_view(), name='mailing_create'),
    path('mailings/<int:pk>/update/', views.MailingUpdateView.as_view(), name='mailing_update'),
    path('mailings/<int:pk>/delete/', views.MailingDeleteView.as_view(), name='mailing_delete'),
    path('mailings/<int:pk>/status/', views.MailingStatusView.as_view(), name='mailing_status'),
    path('mailings/<int:pk>/deactivate/', views.MailingDeactivateView.as_view(), name='mailing_deactivate'),
]

# Маршруты для статистики и логов
stats_and_logs_patterns = [
    path('statistics/', views.StatisticsView.as_view(), name='mailing_statistics'),
    path('logs/', views.MailingLogListView.as_view(), name='mailing_logs'),
    path('attempt-stats/', views.MailingAttemptStatsView.as_view(), name='mailing_attempt_stats'),
    path('attempt-stats/<int:pk>/', views.MailingAttemptDetailView.as_view(), name='mailing_attempt_detail'),
]

# Маршруты для пользователей
user_patterns = [
    path('users/', views.UserListView.as_view(), name='user_list'),
    path('users/<int:pk>/block/', views.UserBlockView.as_view(), name='user_block'),
]

# Главная страница
main_page_patterns = [
    path('', views.MainPageView.as_view(), name='main_page'),
]

# Объединение всех маршрутов
urlpatterns = (
    auth_patterns
    + client_patterns
    + message_patterns
    + mailing_patterns
    + stats_and_logs_patterns
    + user_patterns
    + main_page_patterns
)
