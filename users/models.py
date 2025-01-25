from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils.translation import gettext_lazy as _


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        """
        Создание и сохранение обычного пользователя с email и паролем.
        """
        if not email:
            raise ValueError(_('The Email field must be set'))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """
        Создание и сохранение суперпользователя с email и паролем.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    # Убираем стандартное поле username
    email = models.EmailField(
        unique=True,
        verbose_name=_("Email"),
        help_text=_("Используется для авторизации")
    )
    avatar = models.ImageField(
        upload_to='users/avatars/',
        blank=True,
        null=True,
        verbose_name=_("Аватар"),
        help_text=_("Загрузите изображение профиля")
    )
    phone_number = models.CharField(
        max_length=35,
        blank=False,
        null=False,
        verbose_name=_("Номер телефона"),
        help_text=_("Введите номер телефона")
    )
    country = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name=_("Страна"),
        help_text=_("Укажите страну проживания")
    )
    token = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name=_("Token"),
        help_text=_("Укажите токен для подтверждения")
    )


    USERNAME_FIELD = 'email'  # Устанавливаем email как поле для авторизации
    REQUIRED_FIELDS = []  # Убираем обязательное поле username

    objects = CustomUserManager()  # Используем наш менеджер

    class Meta:
        verbose_name = _("Пользователь")
        verbose_name_plural = _("Пользователи")

    def __str__(self):
        return self.email
