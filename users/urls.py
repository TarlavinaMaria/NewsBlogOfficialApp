from django.urls import path
from .views import RegisterView, LoginView, LogoutView, ProfileView, EditProfileView, AuthorArticlesView, ArticleDetailView, UserActivityView, WebPasswordResetView
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views

# Урлы для авторизации и регистрации пользователей.
urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('profile/edit/', EditProfileView.as_view(), name='edit_profile'),
    path('author/<int:author_id>/articles/', AuthorArticlesView.as_view(), name='author_articles'),
    path('article/<int:pk>/', ArticleDetailView.as_view(), name='article_detail'),
    path('profile/activity/', UserActivityView.as_view(), name='user_activity'),

    path('password_reset/', WebPasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='users/password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='users/password_reset_confirm.html'), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='users/password_reset_complete.html'), name='password_reset_complete'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)