from django.contrib import admin
from .models import News, Tag, Comment
from django.utils.html import format_html
from django.urls import path
from django.shortcuts import render

# Функции для массовых операций с новостями
def make_published(modeladmin, request, queryset):
    # Функция для массового изменения статуса новостей на "Проверено"
    queryset.update(status='published')
make_published.short_description = "Пометить как 'Проверено'"

def make_draft(modeladmin, request, queryset):
    # Функция для массового изменения статуса новостей на "Не проверено"
    queryset.update(status='draft')
make_draft.short_description = "Пометить как 'Не проверено'"

def make_archived(modeladmin, request, queryset):
    # Функция для массового изменения статуса новостей на "Архив"
    queryset.update(status='archived')
make_archived.short_description = "Пометить как 'Архив'"

def add_likes_to_news(modeladmin, request, queryset):
    # Функция для массового добавления лайков текущему пользователю в новостях
    for news in queryset:
        news.likes.add(request.user)
add_likes_to_news.short_description = "Добавить лайк текущему пользователю"

def add_likes_to_comments(modeladmin, request, queryset):
    # Функция для массового добавления лайков текущему пользователю в комментариях
    for comment in queryset:
        comment.likes.add(request.user)
add_likes_to_comments.short_description = "Добавить лайк текущему пользователю"

def remove_likes_from_news(modeladmin, request, queryset):
    # Функция для массового удаления лайков из новостей
    for news in queryset:
        news.likes.clear()
remove_likes_from_news.short_description = "Удалить все лайки"

def remove_likes_from_comments(modeladmin, request, queryset):
    # Функция для массового удаления лайков из комментариев
    for comment in queryset:
        comment.likes.clear()
remove_likes_from_comments.short_description = "Удалить все лайки"

class NewsAdmin(admin.ModelAdmin):
    """Класс для управления новостями в админке"""
    list_display = ('title', 'pub_date', 'status', 'total_likes', 'preview_link') # Поля, которые отображаются в админке
    list_filter = ('status', 'pub_date') # Фильтры для фильтрации новостей по статусу и дате публикации
    search_fields = ('title', 'brief', 'content')  # Поля, по которым будет производиться поиск новостей
    filter_horizontal = ('tags',) # Отображение тегов в виде списка с возможностью выбора нескольких тегов
    exclude = ('likes',)  # Исключаем поле likes из формы
    actions = [make_published, make_draft, make_archived, add_likes_to_news, remove_likes_from_news] # Добавляем действия для массовых операций с новостями

    def preview_link(self, obj):
        """Функция для создания ссылки на предварительный просмотр новости"""
        if obj.id: # Если новость уже сохранена, то создаем ссылку на предварительный просмотр
            return format_html('<a href="{}" target="_blank">Предварительный просмотр</a>', f'/admin/news/news/{obj.id}/preview/')
        else:
            return "Предварительный просмотр недоступен до сохранения новости"
    preview_link.short_description = "Предварительный просмотр"

    def get_urls(self):
        # Переопределяем метод get_urls для добавления ссылки на предварительный просмотр новости
        urls = super().get_urls()
        custom_urls = [
            path('<path:object_id>/preview/', self.admin_site.admin_view(self.preview_view), name='news_preview'),
        ]
        return custom_urls + urls

    def preview_view(self, request, object_id):
        """Функция для отображения страницы предварительного просмотра новости"""
        news = News.objects.get(id=object_id)
        return render(request, 'news/news_preview.html', {'news': news})

    def get_readonly_fields(self, request, obj=None):
        """Функция для добавления поля preview в список только для чтения"""
        readonly_fields = super().get_readonly_fields(request, obj)
        if obj:
            readonly_fields += ('preview',)
        return readonly_fields

    def total_likes(self, obj):
        # Возвращаем количество лайков для каждой новости
        return obj.total_likes()
    total_likes.short_description = "Лайки"

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
    list_display = ('news', 'author', 'content', 'created_at', 'total_likes') # Поля, которые отображаются в списке комментариев в админке
    list_filter = ('news', 'author', 'created_at') # Фильтры для поиска по полю news, author и created_at
    search_fields = ('content', 'author__username')  # Поля, по которым будет производиться поиск
    readonly_fields = ('created_at',)  # Поля, которые нельзя редактировать
    exclude = ('likes',)  # Исключаем поле likes из формы
    actions = [add_likes_to_comments, remove_likes_from_comments] # Добавляем действия для массового добавления и удаления лайков из комментариев

    def total_likes(self, obj):
        # Возвращаем количество лайков для каждого комментария
        return obj.total_likes()
    total_likes.short_description = "Лайки"

    class Meta:
        verbose_name = "Комментарий"
        verbose_name_plural = "Комментарии"

admin.site.register(News, NewsAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Comment, CommentAdmin)