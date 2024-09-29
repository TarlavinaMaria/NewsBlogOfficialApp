from django.db import models
from django.utils import timezone
from django.urls import reverse
from django.contrib.auth.models import User

class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name

class News(models.Model):
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


        