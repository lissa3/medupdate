import os
from io import BytesIO

from django.core.files.base import ContentFile
from django.core.files.uploadedfile import InMemoryUploadedFile, TemporaryUploadedFile
from PIL import Image


def resize(image, WIDTH, HEIGHT):
    size = (WIDTH, HEIGHT)
    if isinstance(image, InMemoryUploadedFile):
        memory_image = BytesIO(image.read())
        pil_image = Image.open(memory_image)

        img_format = os.path.splitext(image.name)[1][1:].upper()
        img_format = "JPEG" if img_format == "JPG" else img_format
        if pil_image.width > WIDTH or pil_image.height > HEIGHT:
            pil_image.thumbnail(size)
        new_image = BytesIO()
        pil_image.save(new_image, format=img_format)
        new_image = ContentFile(new_image.getvalue())
        return InMemoryUploadedFile(
            new_image, None, image.name, image.content_type, None, None
        )
    elif isinstance(image, TemporaryUploadedFile):
        path = image.temporary_file_path()
        pil_image = Image.open(path)

        if pil_image.width > WIDTH or pil_image.height > HEIGHT:
            pil_image.thumbnail(size)
            pil_image.save(path)
            image.size = os.stat(path).st_size
    return image
