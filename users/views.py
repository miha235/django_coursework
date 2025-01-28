from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse_lazy,reverse
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from django.contrib.auth.tokens import default_token_generator as token_generator
from django.core.mail import send_mail
from django.contrib.auth.views import LoginView, LogoutView
from django.views.generic.edit import CreateView
from mailing.forms import CustomUserCreationForm,CustomAuthenticationForm,CustomUser


class SignUpView(CreateView):
    ''' Контроллер для создания нового Пользователя с отправкой email подтверждения '''
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'users/registration/signup.html'

    def form_valid(self, form):
        # Сохранение пользователя, но ещё не активированного
        user = form.save(commit=False)
        user.is_active = False  # Деактивируем пользователя до подтверждения
        user.save()

        # Генерация токена для подтверждения email
        token = token_generator.make_token(user)
        uid = urlsafe_base64_encode(str(user.pk).encode('utf-8')).decode()

        # Отправка email для подтверждения
        current_site = get_current_site(self.request)
        subject = 'Подтвердите вашу почту'
        message = render_to_string('users/activation_email.html', {
            'user': user,
            'domain': current_site.domain,
            'uid': uid,
            'token': token,
        })
        send_mail(subject, message, 'from@example.com', [user.email])
        return render(self.request, 'users/registration/confirmation_sent.html')

# Контроллер для подтверждения email
def verify_email(request, uidb64, token):
    ''' Проверка токена и активация пользователя '''
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = CustomUser.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
        user = None

    if user is not None and token_generator.check_token(user, token):
        user.is_active = True
        user.is_verified = True
        user.save()
        return redirect('login')
    else:
        return render(request, 'users/activation_invalid.html')
'''
def verify_email(request, user_id):
    #Функция проверки верификации пользователя
    user = CustomUser.objects.get(id=user_id)
    user.is_verified = True
    user.save()
    return redirect('login')
'''
class CustomLogoutView(LogoutView):
    success_url = reverse_lazy('main_page')

    def get_success_url(self):
        """Переопределите метод, чтобы перенаправить пользователя после успешного входа."""
        return self.success_url

class CustomLoginView(LoginView):
    ''' Контроллер для логина Пользователя'''
    form_class = CustomAuthenticationForm
    template_name = 'users/registration/login.html'

    def form_valid(self, form):
        remember_me = form.cleaned_data.get('remember_me')
        if not remember_me:
            self.request.session.set_expiry(0)
        return super().form_valid(form)

    def get_success_url(self):
        return self.get_redirect_url() or reverse('client_list')

