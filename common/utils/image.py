from io import BytesIO
from pathlib import Path

from PIL import Image
from django.core.files.uploadedfile import InMemoryUploadedFile

__all__ = [
    'resize_image',
]

DEFAULT_WIDTH = 200
DEFAULT_HEIGHT = 200


def resize_image(image_file, width: int = None, height: int = None, quality=75) -> InMemoryUploadedFile:
    """
    Process InMemoryUploadedFile
    return size: 200x200
    """
    if isinstance(image_file, str):
        image_file = Path(image_file)
    if isinstance(image_file, Path):
        image_file_name = image_file.name
    else:
        image_file_name = image_file.name
    img: Image.Image = Image.open(image_file)

    assert img.format.upper() in ('PNG', 'JPG', 'JPEG')
    img_format = img.format

    mode = img.mode
    if mode not in ('L', 'RGB'):
        if mode == 'RGBA':
            alpha = img.split()[3]
            bgmask = alpha.point(lambda x: 255 - x)
            img = img.convert('RGB')
            # paste(color, box, mask)
            img.paste((255, 255, 255), None, bgmask)
        else:
            img = img.convert('RGB')

    img_width, img_height = img.size
    if any((width, height)):
        # 缺少的宽高参数补全
        if width is None:
            width = height * img_width / img_height
        if height is None:
            height = width * img_height / img_width
    else:
        width = DEFAULT_WIDTH
        height = DEFAULT_HEIGHT

    if width > img_width or height > img_height:
        # 目标宽/高大于原始图片宽高，无法缩小
        try:
            width, height = img_width, img_height
        except Exception as e:
            raise

    # 调整比例
    img_wh_ratio = img_width / img_height
    target_wh_ratio = width / height

    # box：(left, upper, right, lower)
    if target_wh_ratio > img_wh_ratio:
        # 原图宽度不变
        target_height = img_width / target_wh_ratio  # 目标高度（小于原高）
        delta = (img_height - target_height) / 2
        box = (0, delta, img_width, delta + target_height)
        region = img.crop(box)
    elif target_wh_ratio < img_wh_ratio:
        target_width = img_height * target_wh_ratio
        delta = (img_width - target_width) / 2
        box = (delta, 0, delta + target_width, img_height)
        region = img.crop(box)
    else:
        # 比例相同，原图
        region = img

    a = region.resize((width, height), Image.LANCZOS)  # anti-aliasing

    img_io = BytesIO()
    a.save(img_io, img_format, quality=quality)

    try:
        content_type = image_file.content_type
    except AttributeError:
        suffix = Path(image_file_name).suffix.lstrip('.')
        content_type = f'image/{suffix}'

    img_file = InMemoryUploadedFile(
        file=img_io,
        field_name=None,
        name=image_file_name,
        content_type=content_type,
        size=img_io.tell(),
        charset=None
    )
    return img_file
