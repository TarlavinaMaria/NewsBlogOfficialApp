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
    list_display = ('title', 'pub_date', 'status', 'preview_link')
    list_filter = ('status', 'pub_date')
    search_fields = ('title', 'brief', 'content')
    filter_horizontal = ('tags',)
    actions = [make_published, make_draft, make_archived]

    def preview_link(self, obj):
        if obj.id:
            return format_html('<a href="{}" target="_blank">Предварительный просмотр</a>', f'/admin/news/news/{obj.id}/preview/')
        else:
            return "Предварительный просмотр недоступен до сохранения новости"
    preview_link.short_description = "Предварительный просмотр"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('<path:object_id>/preview/', self.admin_site.admin_view(self.preview_view), name='news_preview'),
        ]
        return custom_urls + urls

    def preview_view(self, request, object_id):
        news = News.objects.get(id=object_id)
        return render(request, 'news/news_preview.html', {'news': news})

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = super().get_readonly_fields(request, obj)
        if obj:
            readonly_fields += ('preview',)
        return readonly_fields

    def preview(self, obj):
        if obj.id:
            return format_html('<a href="{}" target="_blank">Предварительный просмотр</a>', f'/admin/news/news/{obj.id}/preview/')
        else:
            return "Предварительный просмотр недоступен до сохранения новости"
    preview.short_description = "Предварительный просмотр"

    class Meta:
        verbose_name = "Новость"
        verbose_name_plural = "Новости"

class TagAdmin(admin.ModelAdmin):
    """Класс для управления тегами в админке"""
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}

    class Meta:
        verbose_name = "Тег"
        verbose_name_plural = "Теги"

class CommentAdmin(admin.ModelAdmin):
    """Класс для управления комментариями в админке"""
    list_display = ('news', 'author', 'content', 'created_at')
    list_filter = ('news', 'author', 'created_at')
    search_fields = ('content', 'author__username')
    readonly_fields = ('created_at',)

    class Meta:
        verbose_name = "Комментарий"
        verbose_name_plural = "Комментарии"

admin.site.register(News, NewsAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Comment, CommentAdmin)