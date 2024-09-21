# your_app/management/commands/export_to_json.py
from django.core.management.base import BaseCommand
from django.core import serializers
from news.models import Tag, News  

# python manage.py export_to_json команда

class Command(BaseCommand):
    help = 'Export data from the database to a JSON file'

    def handle(self, *args, **options):
        # Получаем все объекты моделей
        tags_data = Tag.objects.all()
        news_data = News.objects.all()

        # Объединяем данные из обеих моделей
        combined_data = list(tags_data) + list(news_data)

        # Сериализуем данные в JSON с отступами
        json_data = serializers.serialize('json', combined_data, indent=4)

        # Сохраняем JSON в файл
        with open('base.json', 'w', encoding='utf-8') as json_file:
            json_file.write(json_data)

        self.stdout.write(self.style.SUCCESS('Data exported successfully to base.json'))