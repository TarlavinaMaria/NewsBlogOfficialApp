# Generated by Django 4.2 on 2024-09-22 08:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_profile_default_photo'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='default_photo',
            field=models.ImageField(default='default_photos/default_profile.jpg', upload_to='default_photos/'),
        ),
    ]
