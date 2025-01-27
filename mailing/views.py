from django.utils.decorators import method_decorator
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.views import View
from .models import Client, Message, Mailing, MailingLog
from django.shortcuts import get_object_or_404, render,  redirect
from django.db.models import Count
from .forms import CustomUserCreationForm, CustomAuthenticationForm
from django.contrib.auth.views import LoginView
from django.contrib.auth import login, authenticate, logout
from blog.models import BlogPost
from django.views.decorators.cache import cache_page
from django.shortcuts import redirect
from django import forms
from django.contrib.auth import get_user_model
import logging
from .forms import CustomAuthenticationForm
from django.http import HttpResponseRedirect
from django.urls import reverse

logger = logging.getLogger(__name__)


CustomUser = get_user_model()


@method_decorator(cache_page(60 * 15), name='dispatch')
class MainPageView(TemplateView):
    ''' Контроллер для главной страницы сервиса. Отображает количество рассылок и уникальных клиентов'''
    template_name = 'mailing/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_mailings'] = Mailing.objects.count()
        context['active_mailings'] = Mailing.objects.filter(status='running').count()
        context['unique_clients'] = Client.objects.aggregate(Count('id', distinct=True))['id__count']
        context['random_posts'] = BlogPost.objects.order_by('?')[:3]
        return context


#@method_decorator(cache_page(60 * 5), name='dispatch')
class ClientListView(LoginRequiredMixin, ListView):
    ''' Контроллер для списка уникальных Клиентов для рассылки '''
    model = Client
    template_name = 'mailing/client_list.html'
    context_object_name = 'clients'

    def get_queryset(self):
        if self.request.user.is_superuser:
            return Client.objects.all()
        return Client.objects.filter(owner=self.request.user)


class ClientCreateView(LoginRequiredMixin, CreateView):
    ''' Контроллер для добавления нового Клиента '''
    model = Client
    template_name = 'mailing/client_form.html'
    fields = ['email', 'full_name', 'comment']
    success_url = reverse_lazy('client_list')

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)

class ClientDetailView(LoginRequiredMixin,DetailView):
    ''' Контроллер для отображения свойств выбранного Клиента '''
    model = Client
    template_name = 'mailing/client_detail.html'


class ClientUpdateView(LoginRequiredMixin,UpdateView):
    ''' Контроллер для обновления свойств выбранного Клиента '''
    model = Client
    template_name = 'mailing/client_form.html'
    fields = ['email', 'full_name', 'comment']
    success_url = reverse_lazy('client_list')


class ClientDeleteView(LoginRequiredMixin, DeleteView):
    ''' Контроллер для удаления Клиента '''
    model = Client
    template_name = 'mailing/client_confirm_delete.html'
    success_url = reverse_lazy('client_list')


#@method_decorator(cache_page(60 * 5), name='dispatch') <- кэширование сообщений приводит к тому, что новое сообщение не видно в списке без перезапуска приложения. Увы.
class MessageListView(LoginRequiredMixin,ListView):
    ''' Контроллер для отображения списка Сообщений'''
    model = Message
    template_name = 'mailing/message_list.html'
    context_object_name = 'messages'

    def get_queryset(self):
        if self.request.user.is_superuser:
            return Message.objects.all()
        return Message.objects.filter(owner=self.request.user)

class MessageDetailView(LoginRequiredMixin,DetailView):
    ''' Контроллер для отображения деталей Сообщения'''
    model = Message
    template_name = 'mailing/message_detail.html'


class MessageCreateView(LoginRequiredMixin,CreateView):
    ''' Контроллер для создания нового Сообщения'''
    model = Message
    fields = ['subject', 'body']
    template_name = 'mailing/message_form.html'
    success_url = reverse_lazy('message_list')

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class MessageUpdateView(LoginRequiredMixin,UpdateView):
    '''  Контроллер для формы редактирования деталей Сообщения'''
    model = Message
    template_name = 'mailing/message_form.html'
    fields = ['subject', 'body']
    success_url = reverse_lazy('message_list')


class MessageDeleteView(LoginRequiredMixin,DeleteView):
    ''' Контроллер для удаления Сообщения'''
    model = Message
    template_name = 'mailing/message_confirm_delete.html'
    success_url = reverse_lazy('message_list')


# представления для Mailing
class MailingListView(LoginRequiredMixin, ListView):
    ''' Контроллер для отображения списка Рассылок'''
    model = Mailing
    template_name = 'mailing/mailing_list.html'

    def get_queryset(self):
        if self.request.user.groups.filter(name='Managers').exists(): # админу видны все Рассылки
            return Mailing.objects.all()
        return Mailing.objects.filter(owner=self.request.user) # обычным пользователям - только созданные ими Рассылки


class OwnerRequiredMixin(UserPassesTestMixin):
    ''' Класс-примесь для проверки того, что объект (Рассылка) принадлежит запросившему Пользователю или пользователь относится к группе Менеджеров'''
    def test_func(self):
        obj = self.get_object()
        return obj.owner == self.request.user or self.request.user.groups.filter(name='Managers').exists()


class MailingDetailView(LoginRequiredMixin, OwnerRequiredMixin, DetailView):
    ''' Контроллер для отображения деталей Рассылки. Примесь OwnerRequiredMixin отобрадает только рассылки пользователя; Менеджер видит все рассылки'''
    model = Mailing
    template_name = 'mailing/mailing_detail.html'


class MailingForm(forms.ModelForm):
    ''' Контроллер для формы Рассылки - отоборажает поля: время начала, периодичность, Сообщение, Клиенты, статус'''
    class Meta:
        model = Mailing
        fields = ['start_time', 'periodicity', 'message', 'clients', 'status']
        widgets = {
            'start_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M'),
        }


class MailingUpdateView(LoginRequiredMixin, UpdateView):
    ''' Контроллер для формы редактирования Рассылки'''
    model = Mailing
    form_class = MailingForm
    template_name = 'mailing/mailing_form.html'
    success_url = reverse_lazy('mailing_list')

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        if self.object.status == 'running': # у работающей рассылки нельзя менять время старта и периодичность отправки сообшений - сделать атрибуты readonly
            form.fields['start_time'].widget.attrs['readonly'] = True
            form.fields['periodicity'].widget.attrs['readonly'] = True
        return form

    def form_valid(self, form):
        if self.object.status == 'running':
            # Если рассылка активна, разрешаем изменять только определенные поля
            self.object.message = form.cleaned_data['message']
            self.object.clients.set(form.cleaned_data['clients'])
            self.object.save()
        else:
            form.save()
        return super().form_valid(form)


class MailingCreateView(LoginRequiredMixin, CreateView):
    ''' Контроллер для формы создания Рассылки'''
    model = Mailing
    form_class = MailingForm
    template_name = 'mailing/mailing_form.html'
    success_url = reverse_lazy('mailing_list')

    def form_valid(self, form):
        form.instance.owner = self.request.user
        form.instance.status = 'created'
        return super().form_valid(form)


class MailingDeleteView(LoginRequiredMixin, OwnerRequiredMixin, DeleteView):
    ''' Контроллер для удаления Рассылки'''
    model = Mailing
    template_name = 'mailing/mailing_confirm_delete.html'
    success_url = reverse_lazy('mailing_list')


class MailingStatusView(LoginRequiredMixin, View):
    ''' Контроллер с функцией изменения статуса Рассылки запустить -> приостановить -> возобновить'''
    def post(self, request, pk):
        mailing = get_object_or_404(Mailing, pk=pk)
        action = request.POST.get('action')
        if action == 'start':
            mailing.status = 'running'
        elif action == 'pause':
            mailing.status = 'paused'
        elif action == 'resume':
            mailing.status = 'running'
        mailing.save()
        return redirect('mailing_detail', pk=pk)


class MailingAttemptStatsView(LoginRequiredMixin, ListView):
    ''' Контроллер отображения статистики по отправке Рассылок '''
    model = Mailing
    template_name = 'mailing/mailing_attempt_stats.html'
    context_object_name = 'mailings'

    def get_queryset(self):
        ''' Общее количество отправленных сообщений и количества успешных отправок'''
        return Mailing.objects.annotate(
            total_attempts=Count('attempts'),
            successful_attempts=Count('attempts', filter=models.Q(attempts__status=True))
        )


class MailingAttemptDetailView(LoginRequiredMixin, DetailView):
    ''' Контроллер отображения деталей Рассылки - все Попытки с сортировкой по убыванию даты'''

    model = Mailing
    template_name = 'mailing/mailing_attempt_detail.html'
    context_object_name = 'mailing'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['attempts'] = self.object.attempts.all().order_by('-timestamp')
        return context


class MailingLogListView(LoginRequiredMixin,ListView):
    ''' Контроллер отображения лога Рассылки'''
    model = MailingLog
    template_name = 'mailing/mailing_log_list.html'
    context_object_name = 'logs'
    ordering = ['-timestamp']

    def get_queryset(self):
        if self.request.user.is_superuser:
            return MailingLog.objects.all()
        return MailingLog.objects.filter(mailing__owner=self.request.user)


@method_decorator(cache_page(60 * 15), name='dispatch')
class StatisticsView(TemplateView):
    ''' Контроллер отображения ОБЩЕЙ статистики по отправке Рассылок для всего приложения'''
    template_name = 'mailing/statistics.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_mailings'] = Mailing.objects.count()
        context['active_mailings'] = Mailing.objects.filter(status='running').count()
        context['total_clients'] = Client.objects.count()
        context['total_messages'] = Message.objects.count()

        if context['total_mailings'] > 0:
            context['active_percentage'] = (context['active_mailings'] / context['total_mailings']) * 100
        else:
            context['active_percentage'] = 0

        return context


class ManagerRequiredMixin(UserPassesTestMixin):
    ''' Класс-примесь для управления доступом - проверяет, является ли пользователь менеджером'''
    def test_func(self):
        return self.request.user.groups.filter(name='Managers').exists()


class SignUpView(CreateView):
    ''' Контроллер для создания нового Пользователя'''
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'users/registration/signup.html'


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


def verify_email(request, user_id):
    ''' Функция проверки верификации пользователя'''
    user = CustomUser.objects.get(id=user_id)
    user.is_verified = True
    user.save()
    return redirect('login')

class UserListView(LoginRequiredMixin, ManagerRequiredMixin, ListView):
    ''' Просмотр Пользователей сервиса'''
    model = CustomUser
    template_name = 'mailing/user_list.html'


class ManagerMailingListView(UserPassesTestMixin, ListView):
    model = Mailing
    template_name = 'mailing/manager_mailing_list.html'

    def test_func(self):
        return self.request.user.groups.filter(name='Managers').exists()


class ManagerUserListView(UserPassesTestMixin, ListView):
    model = CustomUser
    template_name = 'mailing/manager_user_list.html'

    def test_func(self):
        return self.request.user.groups.filter(name='Managers').exists()


class UserBlockView(LoginRequiredMixin, ManagerRequiredMixin, UpdateView):
    model = CustomUser
    fields = ['is_active']
    template_name = 'mailing/user_block.html'
    success_url = reverse_lazy('user_list')


class MailingDeactivateView(LoginRequiredMixin, ManagerRequiredMixin, UpdateView):
    model = Mailing
    fields = ['is_active']
    template_name = 'mailing/mailing_deactivate.html'
    success_url = reverse_lazy('mailing_list')


#def custom_logout(request):
#    logout(request)
#    return redirect('main_page')

class CustomLogoutView(LogoutView):
    success_url = reverse_lazy('main_page')

    def get_success_url(self):
        """Переопределите метод, чтобы перенаправить пользователя после успешного входа."""
        return self.success_url



class IndexView(TemplateView):
    template_name = 'mailing/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Выбираем три случайных поста
        total_posts = BlogPost.objects.count()
        if total_posts >= 3:
            context['random_posts'] = BlogPost.objects.order_by('?')[:3]
        else:
            context['random_posts'] = BlogPost.objects.all()

        # Пример данных для статистики
        context['total_mailings'] = 10
        context['active_mailings'] = 5
        context['unique_clients'] = 20
        return context

