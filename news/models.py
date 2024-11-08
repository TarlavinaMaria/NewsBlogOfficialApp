from django.db import models
from django.utils import timezone
from django.urls import reverse
from django.contrib.auth.models import User
from unidecode import unidecode

class Tag(models.Model):
    """Класс для тегов новостей"""
    name = models.CharField(max_length=50, unique=True, verbose_name='Название')
    slug = models.SlugField(max_length=50, unique=True, blank=True, verbose_name='URL')

    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        # Транслитерация имени тега
        self.slug = unidecode(self.name)
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Тег"
        verbose_name_plural = "Теги"

class News(models.Model):
    """Класс для новостей"""
    STATUS_CHOICES = (
        ('draft', 'Не проверено'),
        ('published', 'Проверено'),
        ('archived', 'Архив'),
    )

    title = models.CharField(max_length=200, verbose_name='Заголовок')
    brief = models.TextField(verbose_name='Краткое описание')
    content = models.TextField(verbose_name='Текст новости')
    pub_date = models.DateTimeField(default=timezone.now, verbose_name='Дата публикации')
    views = models.IntegerField(default=0, verbose_name='Просмотры')
    tags = models.ManyToManyField('Tag', blank=True, verbose_name='Теги')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft', verbose_name='Статус')
    image = models.ImageField(upload_to='news_images/', blank=True, null=True, verbose_name='Изображение')
    author = models.ForeignKey(User, on_delete=models.SET_DEFAULT, default=1, verbose_name='Автор')  # Устанавливаем по умолчанию администратора
    notified = models.BooleanField(default=False, verbose_name='Уведомление отправлено')

    def __str__(self):
        return self.title

    def increase_views(self):
        # Добавляем один просмотр к новости при каждом открытии
        self.views += 1
        self.save(update_fields=['views'])

    class Meta:
        verbose_name = "Новость"
        verbose_name_plural = "Новости"


class Comment(models.Model):
    """Модель для комментариев к новостям"""
    news = models.ForeignKey(News, on_delete=models.CASCADE, related_name='comments', verbose_name='Новость')
    author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Автор')
    content = models.TextField(verbose_name='Текст комментария')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    likes = models.ManyToManyField(User, related_name='liked_comments', blank=True, verbose_name='Лайки')

    def __str__(self):
        return f"Комментарий от {self.author.username} к {self.news.title}"

    def total_likes(self):
        return self.likes.count()
    
    class Meta:
        verbose_name = "Комментарий"
        verbose_name_plural = "Комментарии"

        