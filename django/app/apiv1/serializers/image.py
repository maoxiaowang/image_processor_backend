import json
import uuid
from pathlib import Path

import cv2
import numpy as np
from common.utils.json import NumJsonEncoder
from django.core.files.base import ContentFile
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from apiv1.serializers import UserSerializer
from apiv1.utils import generate_thumbnail
from main.models.image import Image, ImageGeneration


class ImageSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Image
        fields = '__all__'


class ImageGenerationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImageGeneration
        fields = '__all__'


class NestedImageSerializer(serializers.ModelSerializer):
    generations = ImageGenerationSerializer(many=True)

    class Meta:
        model = Image
        fields = '__all__'


class NestedImageGenerationSerializer(serializers.ModelSerializer):
    original_image = ImageSerializer()

    class Meta:
        model = ImageGeneration
        fields = '__all__'


class ImageCreateUpdateSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    thumbnail = serializers.ImageField(required=False)

    class Meta:
        model = Image
        fields = ('name', 'image', 'thumbnail', 'user')

    def validate_image(self, image):
        try:
            thumbnail = generate_thumbnail(image)
        except Exception:
            # log here
            raise serializers.ValidationError(
                _('Upload a valid image. The file you uploaded was '
                  'either not an image or a corrupted image.')
            )
        self.thumbnail = thumbnail
        return image

    def validate(self, attrs):
        attrs['thumbnail'] = self.thumbnail
        return attrs


class BaseProcessSerializer(serializers.Serializer):

    def _process(self, image: cv2.typing.MatLike, validated_data: dict):
        raise NotImplementedError

    def update(self, instance, validated_data):
        action = self.__class__.__name__.replace('ImageSerializer', '').lower()
        # 读取文件内容为字节流
        image_bytes = self.instance.image.read()
        # 将字节流转换为 numpy 数组
        np_array = np.frombuffer(image_bytes, dtype=np.uint8)
        # 将 numpy 数组解码为图像
        image = cv2.imdecode(np_array, cv2.IMREAD_COLOR)

        # 图像处理
        umat_image = self._process(image, validated_data)

        suffix = Path(instance.image.name).suffix
        # 将处理后的图像转换为字节流
        _, processed_image_bytes = cv2.imencode(suffix, umat_image)
        processed_image_content = ContentFile(
            processed_image_bytes.tobytes(),
            name=f'{action}_{uuid.uuid4().hex}{suffix}'
        )

        img_generation = ImageGeneration.objects.create(
            action=self.context['action'],
            original_image=instance,
            processed_image=processed_image_content,
        )
        instance.generation_num += 1
        instance.save()
        return img_generation

    def create(self, validated_data):
        raise PermissionError

    def to_representation(self, instance):
        return NestedImageGenerationSerializer(
            instance=instance,
            context={'request': self.context['request']}
        ).data


class CropImageSerializer(BaseProcessSerializer):
    width = serializers.IntegerField()
    height = serializers.IntegerField()

    def _process(self, image: cv2.typing.MatLike, validated_data: dict):
        size = (validated_data['width'], validated_data['height'])
        return cv2.resize(image, size)


class FlipImageSerializer(BaseProcessSerializer):
    axis = serializers.IntegerField()

    def _process(self, image: cv2.typing.MatLike, validated_data: dict):
        axis = validated_data['axis']
        return np.flip(image, axis=axis)


class RotateImageSerializer(BaseProcessSerializer):
    angle = serializers.IntegerField()

    def _process(self, image: cv2.typing.MatLike, validated_data: dict):
        angle = validated_data['angle']
        width, height = self.instance.image.width, self.instance.image.height
        center = (width // 2, height // 2)
        matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
        return cv2.warpAffine(image, matrix, (width, height))


class BlurImageSerializer(BaseProcessSerializer):
    mode = serializers.CharField()

    def _process(self, image: cv2.typing.MatLike, validated_data: dict):
        mode = validated_data['mode']
        if mode == "mean":
            umat = cv2.blur(image, (5, 5))
        elif mode == "median":
            umat = cv2.medianBlur(image, 5)
        elif mode == "gaussian":
            umat = cv2.GaussianBlur(image, (5, 5), 0)
        else:
            raise serializers.ValidationError(f'The value "{mode}" is not a valid mode.')
        return umat


class DetectImageSerializer(BaseProcessSerializer):

    def update(self, instance, validated_data):
        # 读取文件内容为字节流
        image_bytes = self.instance.image.read()
        # 将字节流转换为 numpy 数组
        np_array = np.frombuffer(image_bytes, dtype=np.uint8)
        # 将 numpy 数组解码为图像
        image = cv2.imdecode(np_array, cv2.IMREAD_COLOR)

        info = {
            'width': self.instance.image.width,
            'height': self.instance.image.height,
            'max': np.max(image),
            'min': np.min(image)
        }

        instance.detected_info = json.dumps(info, cls=NumJsonEncoder)
        instance.save()
        return instance

    def to_representation(self, instance):
        return ImageSerializer(instance).data
