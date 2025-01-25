from django.db import models
from django.conf import settings


class Client(models.Model):
    ''' Модель сущности Клиент рассылки (тот, кому будет приходить рассылка) '''
    email = models.EmailField(unique=False)
    full_name = models.CharField(max_length=100)
    comment = models.TextField(blank=True)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self):
        return self.full_name


class Message(models.Model):
    ''' Модель сущности Сообщение - сообщение рассылки, доступное для отправки '''
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


class MailingLog(models.Model):
    ''' Объединенная модель Журнала и Попыток Рассылки '''
    mailing = models.ForeignKey(Mailing, on_delete=models.CASCADE, related_name='logs')
    timestamp = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=[('created', 'Created'), ('running', 'Running'), ('failed', 'Failed')])
    message = models.TextField(blank=True, null=True)
    client = models.ForeignKey(Client, on_delete=models.CASCADE, null=True, blank=True)
    server_response = models.TextField(blank=True, null=True)
    error_message = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Log for Mailing {self.mailing.id} - {self.status}"

    class Meta:
        verbose_name = "Журнал попытки рассылки"
        verbose_name_plural = "Журналы попыток рассылки"
