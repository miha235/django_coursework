from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractUser
from django.conf import settings


class Client(models.Model):
    ''' Модель сущности Клиент рассылки (тот, кому будет приходить рассылка'''
    #pk = models.CompositePrimaryKey("email", "owner") # c версии 5.2!
    id = models.AutoField(
                  auto_created = True,
                  primary_key = True,
                  serialize = False,
                  verbose_name ='ID'
                )
    email = models.EmailField(unique=False)
    full_name = models.CharField(max_length=100)
    comment = models.TextField(blank=True)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self):
        return self.full_name


class Message(models.Model):
    ''' Модель сущности Сообщение - сообщение рассылки, доступное для отправки '''
    #pk = models.CompositePrimaryKey("email", "owner") # c версии 5.2!
    id = models.AutoField(
                  auto_created = True,
                  primary_key = True,
                  serialize = False,
                  verbose_name ='ID'
                )
    subject = models.CharField(max_length=255)
    body = models.TextField()
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self):
        return self.subject


class Mailing(models.Model):
    ''' Модель сущности Рассылка - сообщение рассылки, доступное для отправки '''

    # Периодичности
    PERIOD_CHOICES = [
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('test', 'Test')
    ]

    # Возможные состояния
    STATUS_CHOICES = [
        ('created', 'Created'),
        ('running', 'Running'),
        ('paused', 'Paused'),
        ('completed', 'Completed'),
    ]

    start_time = models.DateTimeField()
    periodicity = models.CharField(max_length=10, choices=PERIOD_CHOICES)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='created')
    message = models.ForeignKey(Message, on_delete=models.CASCADE)
    clients = models.ManyToManyField(Client)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        '''Сохранение рассылки + отметка в журнале '''
        super().save(*args, **kwargs)
        MailingLog.objects.create(
            mailing=self,
            status='created',
            message=f'Mailing {self.id} created'
        )
    def __str__(self):
        return f"Mailing {self.id} - {self.status}"


class MailingAttempt(models.Model):
    ''' Модель Попыток Рассылки - сообщение + клиенты, время начала, статус (активна или нет), ответ сервера и сообщение об ошибке'''
    mailing = models.ForeignKey(Mailing, related_name='attempts', on_delete=models.CASCADE)
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    status = models.BooleanField()
    server_response = models.TextField(blank=True, null=True)
    error_message = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Attempt for Mailing {self.mailing.id} to {self.client.email}"


class MailingLog(models.Model):
    ''' Модель Журнала Рассылок - ссылка на таблицу рассылок, время события, статус, сообщение'''
    mailing = models.ForeignKey(Mailing, on_delete=models.CASCADE, related_name='logs')
    timestamp = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20)
    message = models.TextField()

    def __str__(self):
        return f"Log for Mailing {self.mailing.id} - {self.status}"


class BlogPost(models.Model):
    "Это остатки от шаблонного проекта блога? Можно убрать?"
    title = models.CharField(max_length=200, verbose_name="Заголовок")
    content = models.TextField(verbose_name="Содержимое статьи")
    image = models.ImageField(upload_to='mailing_images/', blank=True, null=True, verbose_name="Изображение")
    views_count = models.PositiveIntegerField(default=0, verbose_name="Количество просмотров")
    pub_date = models.DateTimeField(auto_now_add=True, verbose_name="Дата публикации")
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='mailing_posts', verbose_name="Автор")

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Статья рассылки"
        verbose_name_plural = "Статьи рассылки"