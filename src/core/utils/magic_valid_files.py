import magic
from django.core.exceptions import ValidationError


def validate_img_mimetype(img):
    """validation user image for avatar
    let op: docs expect a path -> change it"""
    allowed_mime_types = [
        "image/jpg",
        "image/jpeg",
        "image/png",
    ]
    upload_img_mime = magic.from_buffer(img.read(2048), mime=True)
    if upload_img_mime not in allowed_mime_types:
        raise ValidationError("Unsupported image type")
