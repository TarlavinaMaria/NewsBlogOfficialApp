from django.shortcuts import render, redirect
from django.views.generic import View
from django.contrib.auth import login, authenticate, logout
from .forms import RegistrationForm, LoginForm
from .forms import ProfileForm
from .models import Profile

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
                form.add_error(None, 'Пользователь с этими данными не найден, проверьте данные')
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
        request.session.flush() # Удаляем все данные сессии
        return redirect('news_list')
    
class ProfileView(View):
    def get(self, request):
        try:
            profile = request.user.profile
        except Profile.DoesNotExist:
            profile = Profile.objects.create(user=request.user)
        form = ProfileForm(instance=profile)
        return render(request, 'users/profile.html', {'form': form, 'profile': profile})

    def post(self, request):
        try:
            profile = request.user.profile
        except Profile.DoesNotExist:
            profile = Profile.objects.create(user=request.user)
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('profile')
        return render(request, 'users/profile.html', {'form': form, 'profile': profile})