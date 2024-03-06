from django.db.models import Q
from rest_framework import generics, status
from rest_framework.exceptions import ValidationError, PermissionDenied
from rest_framework.response import Response

from apiv1.serializers import image as image_serializers
from apiv1.utils import generate_thumbnail
from apiv1.views.mixin import SingleObjectIdentityCheckMixin, MultipleObjectsIdentityCheckMixin
from common.views.mixins import CreateMixin, UpdateMixin
from main.models.image import Image, ImageGeneration


class ListCreateImageView(CreateMixin, generics.ListCreateAPIView):
    queryset = Image.objects.all()
    create_serializer_class = image_serializers.ImageCreateSerializer
    serializer_class = image_serializers.ImageSerializer

    def get_queryset(self):
        return Image.objects.filter(
            Q(user=self.request.user) | Q(is_public=True)
        )

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class RetrieveUpdateDestroyImageView(UpdateMixin, generics.RetrieveUpdateDestroyAPIView):
    queryset = Image.objects.all()
    update_serializer_class = image_serializers.ImageUpdateSerializer
    serializer_class = image_serializers.NestedImageSerializer

    def perform_destroy(self, instance):
        return super().perform_destroy(instance)


class DeleteMultiImageView(MultipleObjectsIdentityCheckMixin, generics.DestroyAPIView):
    queryset = Image.objects.all()

    def delete(self, request, *args, **kwargs):
        image_ids = kwargs['image_ids']
        images = Image.objects.filter(id__in=image_ids)
        for image in images:
            # Delete associated files
            image.image.delete(save=False)
            image.thumbnail.delete(save=False)
            for gen in image.generations.all():
                gen.processed_image.delete(save=False)

        images.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ProcessImageView(generics.UpdateAPIView):
    queryset = Image.objects.all()

    def get_serializer_class(self):
        action: str = self.kwargs['action']
        try:
            cls = getattr(image_serializers, f'{action.capitalize()}ImageSerializer')
        except AttributeError:
            raise ValidationError(f'The action {action} is not valid.')
        return cls

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['action'] = self.kwargs['action'].upper()
        return context

    def put(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        try:
            serializer.is_valid(raise_exception=True)
        except Exception as e:
            print(e)
            raise
        serializer.save()
        return Response(data=serializer.data)


class ElevateGenerationImageView(generics.UpdateAPIView):
    queryset = ImageGeneration.objects.all()

    def put(self, request, *args, **kwargs):
        instance: ImageGeneration = self.get_object()
        thumbnail = generate_thumbnail(instance.processed_image.file)
        image = Image.objects.create(
            name=f'{instance.action.lower().capitalize()}_{instance.id}',
            user=self.request.user,
            image=instance.processed_image,
            generated_action=instance.action,
            thumbnail=thumbnail,
            width=instance.width,
            height=instance.height
        )
        data = image_serializers.ImageSerializer(image).data
        return Response(data)
