from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse_lazy, reverse
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from django.contrib.auth.tokens import default_token_generator as token_generator
from django.core.mail import send_mail
from django.contrib.auth.views import LoginView, LogoutView
from django.views.generic.edit import CreateView
from mailing.forms import CustomUserCreationForm, CustomAuthenticationForm, CustomUser

class SignUpView(CreateView):
    ''' Контроллер для регистрации нового пользователя '''
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'users/registration/signup.html'

    def form_valid(self, form):
        # Создаём пользователя, но пока не активируем
        user = form.save(commit=False)
        user.is_active = False
        user.save()

        # Генерация токена и ID пользователя
        token = token_generator.make_token(user)
        uid = urlsafe_base64_encode(str(user.pk).encode('utf-8'))

        # Домен текущего сайта
        current_site = get_current_site(self.request)

        # Формируем email-сообщение
        subject = 'Подтверждение профиля'
        message = render_to_string('users/registration/activation_email.html', {
            'user': user,
            'username': user.username,
            'domain': current_site.domain,
            'uid': uid,
            'token': token,
        })

        # Извлекаем ссылку из HTML-сообщения (можно сделать это вручную или оставить как есть)
        activation_link = f"http://{current_site.domain}/users/verify/{urlsafe_base64_encode ( str ( user.pk ).encode ( 'utf-8' ) )}/{token}/"
        message_plain = f"Здравствуйте, {user.username}!\n\n" \
                        f"Спасибо за регистрацию на нашем сайте. Чтобы активировать свой профиль, перейдите по следующей ссылке:\n\n" \
                        f"{activation_link}\n\n" \
                        "Если вы не регистрировались на нашем сайте, просто проигнорируйте это письмо."

        # Отправка email
        send_mail(
            subject, message_plain, 'v_23_d_1989@mail.ru', [user.email], fail_silently=False
        )

        # Возвращаем страницу подтверждения
        return render(self.request, 'users/registration/conformation_sent.html')


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
        user.is_verified = True  # Если в модели есть это поле
        user.save()
        return redirect('login')
    else:
        return render(request, 'users/registration/activation_invalid.html')


class CustomLogoutView(LogoutView):
    ''' Контроллер для выхода пользователя '''
    next_page = reverse_lazy('main_page')


class CustomLoginView(LoginView):
    ''' Контроллер для входа пользователя '''
    form_class = CustomAuthenticationForm
    template_name = 'users/registration/login.html'

    def form_valid(self, form):
        remember_me = form.cleaned_data.get('remember_me')
        if not remember_me:
            self.request.session.set_expiry(0)
        return super().form_valid(form)

    def get_success_url(self):
        return self.get_redirect_url() or reverse('client_list')
