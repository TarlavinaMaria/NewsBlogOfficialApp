import asyncio

from django.db.models.signals import post_save, post_migrate
from django.dispatch import receiver

from news_blog.settings import TELEGRAM_BOT_TOKEN, YOUR_PERSONAL_CHAT_ID
from news.models import News
from .telegram_bot import send_telegram_message

from django.contrib.auth.models import Group, Permission, User
from django.contrib.contenttypes.models import ContentType
from news.models import News, Comment


@receiver(post_save, sender=News)
def send_telegram_notification(sender, instance, created, **kwargs):
    if created and not instance.notified and instance.status == 'draft':

        # Форматирование даты публикации
        pub_date_formatted = instance.pub_date.strftime('%d.%m.%Y %H:%M')
        
        # Ограничение длины текста новости
        content_truncated = (instance.content[:100] + '...') if len(instance.content) > 100 else instance.content

        # Формируем сообщение с полной информацией о новости
        message_template = (
            f"Новая новость предложена:\n\n"
            f"Заголовок: {instance.title}\n"
            f"Краткое описание: {instance.brief}\n"
            f"Текст новости: {content_truncated}\n"
            f"Дата публикации: {pub_date_formatted}\n"
            f"Изображение: {'Да' if instance.image else 'Нет'}\n"
            f"Автор: {instance.author.username}"
        )
        
        message = '*Новая новость!*\n' + message_template

        # Отправляем уведомление в Telegram
        asyncio.run(send_telegram_message(TELEGRAM_BOT_TOKEN, YOUR_PERSONAL_CHAT_ID, message))
        
        # Устанавливаем флаг notified в True после отправки уведомления
        instance.notified = True
        instance.save(update_fields=['notified'])


@receiver(post_migrate)
def create_moderators(sender, **kwargs):
    # Проверяем, что миграция выполняется для нужного приложения
    if sender.name == 'news':
        # Создаем группу "Модераторы"
        moderator_group, created = Group.objects.get_or_create(name='Модераторы')

        # Получаем ContentType для моделей News и Comment
        news_content_type = ContentType.objects.get_for_model(News)
        comment_content_type = ContentType.objects.get_for_model(Comment)

        # Получаем разрешения для моделей News и Comment
        news_permissions = Permission.objects.filter(content_type=news_content_type)
        comment_permissions = Permission.objects.filter(content_type=comment_content_type)

        # Добавляем разрешения в группу "Модераторы"
        for permission in news_permissions:
            moderator_group.permissions.add(permission)

        for permission in comment_permissions:
            moderator_group.permissions.add(permission)

        # Сохраняем группу
        moderator_group.save()

        # Создаем модераторов
        moderator1 = User.objects.create_user(username='moderator1', password='password1')
        moderator2 = User.objects.create_user(username='moderator2', password='password2')

        # Добавляем модераторов в группу "Модераторы"
        moderator_group.user_set.add(moderator1)
        moderator_group.user_set.add(moderator2)

        print('Модераторы успешно созданы и добавлены в группу "Модераторы"')