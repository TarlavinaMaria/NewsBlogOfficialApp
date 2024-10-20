from django.urls import path
from .views import RegisterView, LoginView, LogoutView, ProfileView, EditProfileView, AuthorArticlesView, ArticleDetailView
from django.conf import settings
from django.conf.urls.static import static

# Урлы для авторизации и регистрации пользователей.
urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('profile/edit/', EditProfileView.as_view(), name='edit_profile'),
    path('author/<int:author_id>/articles/', AuthorArticlesView.as_view(), name='author_articles'),
    path('article/<int:pk>/', ArticleDetailView.as_view(), name='article_detail'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)