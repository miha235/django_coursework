from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from django.contrib.auth.tokens import default_token_generator as token_generator
from django.core.mail import send_mail
from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.contrib.auth import login

# Регистрация пользователя
def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()

            # Генерация токена для подтверждения email
            token = token_generator.make_token(user)
            uid = urlsafe_base64_encode(user.pk.encode('utf-8')).decode()

            # Отправка email для подтверждения
            subject = 'Подтвердите вашу почту'
            message = render_to_string('users/activation_email.html', {
                'user': user,
                'domain': get_current_site(request).domain,
                'uid': uid,
                'token': token,
            })

            send_mail(subject, message, 'from@example.com', [user.email])

            return HttpResponse('Письмо с подтверждением отправлено.')
    else:
        form = UserCreationForm()

    return render(request, 'users/register.html', {'form': form})
