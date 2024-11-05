from django.shortcuts import render, redirect
from django.views.generic import View, ListView, DetailView
from django.contrib.auth.views import PasswordResetView
from news.models import News
from django.contrib.auth import login, authenticate, logout, get_user_model
from .forms import RegistrationForm, LoginForm
from .forms import ProfileForm
from .models import Profile
from datetime import date
from news.models import Comment
from django.urls import reverse_lazy
from django.contrib import messages
from django.conf import settings


class RegisterView(View):
    """Регистрация"""

    def get(self, request):
        """
        При GET-запросе создается пустая форма RegistrationForm.
        Форма передается в шаблон users/register.html, который отображается пользователю.
        """
        form = RegistrationForm()
        return render(request, 'users/register.html', {'form': form})

    def post(self, request):
        """
        При POST-запросе создается форма RegistrationForm, заполненная данными из запроса (request.POST).
        Если форма валидна (form.is_valid()), создается новый пользователь (form.save()), и пользователь автоматически входит в систему (login(request, user)).
        После успешной регистрации пользователь перенаправляется на страницу входа (redirect('login')).
        Если форма невалидна, она снова отображается пользователю с ошибками.
        """
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Создаем профиль пользователя автоматически
            Profile.objects.create(user=user)
            login(request, user)
            return redirect('news_list')
        return render(request, 'users/register.html', {'form': form})


class LoginView(View):
    """Авторизация"""

    def get(self, request):
        """
        При GET-запросе создается пустая форма LoginForm.
        Форма передается в шаблон users/login.html, который отображается пользователю.
        """
        form = LoginForm()
        return render(request, 'users/login.html', {'form': form})

    def post(self, request):
        """
        При POST-запросе создается форма LoginForm, заполненная данными из запроса (request.POST).
        Если форма валидна (form.is_valid()), извлекаются имя пользователя и пароль (form.cleaned_data.get('username') и form.cleaned_data.get('password')).
        Пользователь аутентифицируется с помощью функции authenticate(username=username, password=password).
        Если аутентификация успешна (user is not None), пользователь входит в систему (login(request, user)), и он перенаправляется на страницу со списком новостей (redirect('news_list')).
        Если аутентификация не удалась, добавляется общая ошибка к форме (form.add_error(None, 'Неверный логин или пароль')), и форма снова отображается пользователю с ошибками.
        """
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('news_list')
            else:
                form.add_error(
                    None, 'Пользователь с этими данными не найден, проверьте данные')
        return render(request, 'users/login.html', {'form': form})


class LogoutView(View):
    """Выход"""

    def get(self, request):
        """
        При GET-запросе пользователь выходит из системы с помощью функции logout(request).
        После выхода пользователь перенаправляется на страницу со списком новостей (redirect('news_list')).
        Удаляются все данные сессии с помощью request.session.flush().
        """
        logout(request)
        request.session.flush()  # Удаляем все данные сессии
        return redirect('news_list')


class ProfileView(View):
    """Профиль пользователя"""

    def get(self, request):
        """
        При GET-запросе извлекается профиль пользователя (profile = request.user.profile).
        Если профиль пользователя не существует (Profile.DoesNotExist), создается новый профиль (Profile.objects.create(user=request.user)).
        Создается форма ProfileForm, связанная с профилем пользователя (form = ProfileForm(instance=profile)).
        Если дата рождения пользователя установлена (profile.date_of_birth), вычисляется возраст пользователя (age = today.year - profile.date_of_birth.year - ((today.month, today.day) < (profile.date_of_birth.month, profile.date_of_birth.day))).
        Форма, профиль пользователя и возраст передаются в шаблон users/profile.html, который отображается пользователю.
        """
        try:
            profile = request.user.profile
        except Profile.DoesNotExist:
            profile = Profile.objects.create(user=request.user)
        form = ProfileForm(instance=profile)
        age = None
        if profile.date_of_birth:
            today = date.today()
            age = today.year - profile.date_of_birth.year - \
                ((today.month, today.day) <
                 (profile.date_of_birth.month, profile.date_of_birth.day))
        return render(request, 'users/profile.html', {'form': form, 'profile': profile, 'age': age})

    def post(self, request):
        """ 
        Обновление профиля пользователя. 
        Если форма валидна, извлекаются имя пользователя и пароль.
        """
        try:
            profile = request.user.profile
        except Profile.DoesNotExist:
            profile = Profile.objects.create(user=request.user)
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('profile')
        return render(request, 'users/profile.html', {'form': form, 'profile': profile})


class EditProfileView(View):
    """Редактирование профиля пользователя"""

    def get(self, request):
        """
        При GET-запросе извлекается профиль пользователя (profile = request.user.profile).
        Если профиль пользователя не существует (Profile.DoesNotExist), создается новый профиль (Profile.objects.create(user=request.user)).
        Создается форма ProfileForm, связанная с профилем пользователя (form = ProfileForm(instance=profile)).
        Форма и профиль пользователя передаются в шаблон users/edit_profile.html, который отображается пользователю.
        """
        try:
            profile = request.user.profile
        except Profile.DoesNotExist:
            profile = Profile.objects.create(user=request.user)
        form = ProfileForm(instance=profile)
        return render(request, 'users/edit_profile.html', {'form': form})

    def post(self, request):
        """
        При POST-запросе извлекается профиль пользователя (profile = request.user.profile).
        Если профиль пользователя не существует (Profile.DoesNotExist), создается новый профиль (Profile.objects.create(user=request.user)).
        Создается форма ProfileForm, связанная с профилем пользователя (form = ProfileForm(request.POST, request.FILES, instance=profile)).
        Если форма валидна, сохраняются изменения в профиле пользователя (form.save()).
        Пользователь перенаправляется на страницу профиля (redirect('profile')).
        В противном случае, отображается форма с ошибками (render(request, 'users/edit_profile.html', {'form': form})).
        """
        try:
            profile = request.user.profile
        except Profile.DoesNotExist:
            profile = Profile.objects.create(user=request.user)
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('profile')
        return render(request, 'users/edit_profile.html', {'form': form})

class AuthorArticlesView(ListView):
    """Просмотр статей автора"""
    model = News
    template_name = 'users/author_articles.html'
    context_object_name = 'articles'
    paginate_by = 10  # Пагинация, если статей много

    def get_queryset(self):
        """Фильтрация статей по автору и статусу"""
        queryset = News.objects.filter(author_id=self.kwargs['author_id']) # Фильтрует статьи по author_id, который передается через URL.
        status = self.request.GET.get('status', 'all') # Получает значение параметра status из GET-запроса. Если параметр не указан, по умолчанию используется значение 'all'.
        if status != 'all': # Если статус не равен 'all', фильтрует статьи по статусу.
            queryset = queryset.filter(status=status)
        return queryset.order_by('-pub_date') # Сортирует статьи по дате публикации в порядке убывания.

    def get_context_data(self, **kwargs):
        """ Добавляет в контекст данные о статусе статей"""
        context = super().get_context_data(**kwargs)
        context['status'] = self.request.GET.get('status', 'all')
        return context
    
class ArticleDetailView(DetailView):
    """Просмотр статьи"""
    model = News
    template_name = 'users/article_detail.html'
    context_object_name = 'article'

class UserActivityView(ListView):
    """Просмотр активности пользователя"""
    model = Comment
    template_name = 'users/user_activity.html'
    context_object_name = 'comments'

    def get_queryset(self):
        """Фильтрация комментариев по пользователю"""
        return Comment.objects.filter(likes=self.request.user).order_by('-created_at')

    def get_context_data(self, **kwargs):
        """Добавляет в контекст данные о пользователе"""
        context = super().get_context_data(**kwargs)
        context['user_comments'] = Comment.objects.filter(author=self.request.user).order_by('-created_at')
        return context

User = get_user_model()

class WebPasswordResetView(PasswordResetView):
    template_name = 'users/password_reset.html'
    email_template_name = 'users/password_reset_email.html'
    subject_template_name = 'users/password_reset_subject.txt'
    success_url = reverse_lazy('password_reset_done')

    def form_valid(self, form):
        email = form.cleaned_data['email']
        if not User.objects.filter(email=email).exists():
            messages.error(self.request, 'Пользователь с таким email не найден.')
            return redirect('password_reset')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['site_name'] = settings.SITE_NAME
        return context