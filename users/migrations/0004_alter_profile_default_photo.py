# Generated by Django 4.2 on 2024-09-27 03:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_alter_profile_default_photo'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='default_photo',
            field=models.ImageField(default='default_photos/default_profile.ico', upload_to='default_photos/'),
        ),
    ]