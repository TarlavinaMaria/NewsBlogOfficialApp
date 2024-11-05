from django.core.management.base import BaseCommand
from news.models import Tag
from unidecode import unidecode

class Command(BaseCommand):
    help = 'Transliterate existing tags'

    def handle(self, *args, **kwargs):
        tags = Tag.objects.all()
        for tag in tags:
            tag.slug = unidecode(tag.name)
            tag.save()
        self.stdout.write(self.style.SUCCESS('Successfully transliterated tags'))