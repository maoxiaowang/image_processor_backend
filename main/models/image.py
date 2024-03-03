import uuid
from pathlib import Path

from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone

User = get_user_model()


IMAGE_PATH = Path('image')


def image_upload_to(_, filename):
    dt_str = timezone.localtime().strftime('%Y%m%d_%H%M%S')
    filename = Path(filename)
    return IMAGE_PATH / 'image' / f'{filename.stem}_{dt_str}{filename.suffix}'


def thumbnail_upload_to(_, filename):
    return IMAGE_PATH / 'thumbnail' / f'{uuid.uuid4().hex}{Path(filename).suffix}'


def generation_upload_to(instance, filename):
    return IMAGE_PATH / 'generation' / instance.action.lower() / f'{uuid.uuid4().hex}{Path(filename).suffix}'


class Image(models.Model):
    name = models.CharField(max_length=255)
    user = models.ForeignKey(User, models.SET_NULL, null=True)
    image = models.ImageField(upload_to=image_upload_to, width_field='width', height_field='height')
    thumbnail = models.ImageField(upload_to=thumbnail_upload_to)
    generated_action = models.CharField(max_length=32, null=True, blank=True)
    generation_num = models.PositiveIntegerField(default=0)
    width = models.IntegerField(blank=True, null=True)
    height = models.IntegerField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'main_image'
        ordering = ('-id',)


class ImageGeneration(models.Model):
    action = models.CharField(max_length=255)
    original_image = models.ForeignKey(Image, models.CASCADE, related_name='generations')
    processed_image = models.ImageField(upload_to=generation_upload_to, width_field='width', height_field='height')
    width = models.IntegerField(blank=True, null=True)
    height = models.IntegerField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'main_image_generation'
        ordering = ('-id',)
