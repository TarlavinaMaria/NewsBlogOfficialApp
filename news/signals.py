import asyncio

from django.db.models.signals import post_save
from django.dispatch import receiver

from news_blog.settings import TELEGRAM_BOT_TOKEN, YOUR_PERSONAL_CHAT_ID
from news.models import News
from .telegram_bot import send_telegram_message


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