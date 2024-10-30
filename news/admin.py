from django.contrib import admin
from .models import News, Tag, Comment
from django.utils.html import format_html
from django.urls import path
from django.shortcuts import render

# Функции для массовых операций с новостями
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
    """Класс для управления новостями в админке"""
    list_display = ('title', 'pub_date', 'status')
    list_filter = ('status', 'pub_date')
    search_fields = ('title', 'brief', 'content')
    filter_horizontal = ('tags',)
    actions = [make_published, make_draft, make_archived]
    readonly_fields = ('preview',)

    def preview(self, obj):
        return format_html('<a href="{}" target="_blank">Предварительный просмотр</a>', f'/admin/news/news/{obj.id}/preview/')

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('<path:object_id>/preview/', self.admin_site.admin_view(self.preview_view), name='news_preview'),
        ]
        return custom_urls + urls

    def preview_view(self, request, object_id):
        news = News.objects.get(id=object_id)
        return render(request, 'news/news_preview.html', {'news': news})

class CommentAdmin(admin.ModelAdmin):
    """Класс для управления комментариями в админке"""
    list_display = ('news', 'author', 'content', 'created_at')
    list_filter = ('news', 'author', 'created_at')
    search_fields = ('content', 'author__username')
    readonly_fields = ('created_at',)

admin.site.register(News, NewsAdmin)
admin.site.register(Tag)
admin.site.register(Comment, CommentAdmin)  # Регистрируем модель Comment с классом CommentAdmin