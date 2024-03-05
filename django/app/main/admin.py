from django.contrib import admin

from main.models import Image, ImageGeneration


# Register your models here.
@admin.register(Image)
class ImageAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'user', 'thumbnail', 'width', 'height', 'created_at']
    list_filter = ['name']
    list_per_page = 20
    list_display_links = ['id', 'name']


@admin.register(ImageGeneration)
class ImageGenerationAdmin(admin.ModelAdmin):
    list_display = ['id', 'action', 'processed_image', 'width', 'height', 'created_at']
    list_filter = ['action']
    list_per_page = 20
    list_display_links = ['id']
