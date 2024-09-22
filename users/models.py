from django.db import models
from django.contrib.auth.models import User
from PIL import Image

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100, blank=True)
    middle_name = models.CharField(max_length=100, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    photo = models.ImageField(upload_to='profile_photos/', null=True, blank=True)
    default_photo = models.ImageField(upload_to='default_photos/', default='default_photos/default_profile.ico')

    def __str__(self):
        return self.user.username

    def get_photo_url(self):
        return self.photo.url if self.photo else self.default_photo.url

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        if self.photo:
            img = Image.open(self.photo.path)
            if img.height > 300 or img.width > 300:
                output_size = (300, 300)
                img.thumbnail(output_size)
                img.save(self.photo.path)