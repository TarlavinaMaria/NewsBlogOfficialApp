from django.contrib import admin
from .models import News, Tag
from django.utils.html import format_html
from django.urls import path
from django.shortcuts import render

"""
    Функции для массовых операций с новостями
"""

def make_published(modeladmin, request, queryset):
    queryset.update(status='published')


make_published.short_description = "Пометить как 'Проверено'"


def make_draft(modeladmin, request, queryset):
    queryset.update(status='draft')


make_draft.short_description = "Пометить как 'Не проверено'"


def make_archived(modeladmin, request, queryset):
    queryset.update(status='archived')


make_archived.short_description = "Пометить как 'Архив'"


class NewsAdmin(admin.ModelAdmin):
    """
    Класс для управления новостями в админке
    """
    list_display = ('title', 'pub_date', 'status')
    list_filter = ('status', 'pub_date')
    search_fields = ('title', 'brief', 'content')

    """Определяет поля с Many-to-Many отношениями, которые будут отображаться с использованием горизонтального фильтра"""
    filter_horizontal = ('tags',)
    
    """Определяет дополнительные действия, которые можно выполнять с выбранными новостями"""
    actions = [make_published, make_draft, make_archived]
    """Предварительный просмотр новости."""
    readonly_fields = ('preview',)

    def preview(self, obj):
        """Возвращает HTML-код ссылки на предварительный просмотр новости."""
        return format_html('<a href="{}" target="_blank">Предварительный просмотр</a>', f'/admin/news/news/{obj.id}/preview/')

    def get_urls(self):
        """Расширяет список URL-адресов админ-панели, добавляя собственный URL для предварительного просмотра новости"""
        urls = super().get_urls()
        custom_urls = [
            path('<path:object_id>/preview/',
                 self.admin_site.admin_view(self.preview_view), name='news_preview'),
        ]
        return custom_urls + urls

    def preview_view(self, request, object_id):
        """Обрабатывает запрос на предварительный просмотр новости и возвращает HTML-страницу с предварительным просмотром."""
        news = News.objects.get(id=object_id)
        return render(request, 'news/news_preview.html', {'news': news})


admin.site.register(News, NewsAdmin)
admin.site.register(Tag)
