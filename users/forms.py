# users/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class RegistrationForm(UserCreationForm):
    """
    RegistrationForm наследуется от UserCreationForm, который является встроенной формой Django для создания нового пользователя. 
    Эта форма уже включает поля для имени пользователя и двух паролей (для подтверждения).
    """
    email = forms.EmailField(required=True) # Это поле позволяет пользователю вводить свой email при регистрации. Параметр required=True указывает, что это поле обязательно для заполнения.

    class Meta:
        """
        Класс Meta указывается модель, с которой связана форма (model = User), и список полей, которые должны быть включены в форму fields.
        """
        model = User
        fields = ("username", "email", "password1", "password2")

class LoginForm(forms.Form):
    """
    LoginForm наследуется от базового класса forms.Form, который предоставляет базовые возможности для создания форм в Django.
    password — это текстовое поле, но с использованием виджета forms.PasswordInput. 
    Виджет PasswordInput отображает вводимые символы как точки или звездочки, чтобы пароль не был виден на экране.
    """
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)