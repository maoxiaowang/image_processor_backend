from common.utils.image import resize_image


def generate_thumbnail(image, width=128, height=128):
    thumbnail = resize_image(image, width=width, height=height)
    return thumbnail
