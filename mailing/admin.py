from django.contrib import admin
from django.contrib.auth import get_user_model
from .models import Client, Message, Mailing, MailingLog

CustomUser = get_user_model()

admin.site.register(Client)
admin.site.register(Message)
admin.site.register(Mailing)
admin.site.register(MailingLog)