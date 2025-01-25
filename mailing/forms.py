from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import Message, Client, Mailing

# Получаем кастомную модель пользователя
CustomUser = get_user_model()

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = CustomUser
        fields = UserCreationForm.Meta.fields + ('email',)


class CustomAuthenticationForm(AuthenticationForm):
    class Meta:
        model = CustomUser


# Форма для создания или редактирования сообщений
class MessageForm(forms.ModelForm):
    ''' Форма для создания или редактирования сообщений '''
    class Meta:
        model = Message
        fields = ['subject', 'body']
        widgets = {
            'body': forms.Textarea(attrs={'rows': 5, 'cols': 40}),
            'subject': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter subject'}),
        }
        labels = {
            'subject': 'Subject of the message',
            'body': 'Body of the message',
        }


# Форма для создания или редактирования клиентов
class ClientForm(forms.ModelForm):
    ''' Форма для создания или редактирования клиентов '''
    class Meta:
        model = Client
        fields = ['email', 'full_name', 'comment']
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter full name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter email'}),
            'comment': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Add comment'}),
        }
        labels = {
            'email': 'Client email',
            'full_name': 'Full name',
            'comment': 'Comment',
        }


# Форма для создания или редактирования рассылок
class MailingForm(forms.ModelForm):
    ''' Форма для создания или редактирования рассылок '''
    class Meta:
        model = Mailing
        fields = ['start_time', 'periodicity', 'message', 'clients']
        widgets = {
            'start_time': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'clients': forms.SelectMultiple(attrs={'class': 'form-control'}),
            'periodicity': forms.Select(attrs={'class': 'form-control'}),
        }
        labels = {
            'start_time': 'Start time',
            'periodicity': 'Periodicity',
            'message': 'Message',
            'clients': 'Clients',
        }
