from django.urls import path
from .views import RegisterView, LoginView, LogoutView

# Урлы для авторизации и регистрации пользователей.
urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
]