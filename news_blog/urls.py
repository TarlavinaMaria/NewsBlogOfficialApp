from django.contrib import admin
from django.urls import path, include

admin.site.site_header = 'Управление новостным блогом'  # текст в шапке админ. панели
admin.site.site_title = 'Админ. панель для новостного блога'  # текст в тайтле браузерадмин. панели
admin.site.index_title = 'Добро пожаловать в панель управления!'  # текст на главной странице админ. панели

# Урлы для приложения news:

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('news.urls')),
    path('users/', include('users.urls')),
]