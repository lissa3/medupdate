import io
import os
from datetime import date, datetime, timedelta
from pathlib import Path
from uuid import uuid4

import pytz
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image


def file_generate_name(original_file_name):
    extension = Path(original_file_name).suffix
    return f"{uuid4().hex}{extension}"


def upload_img(instance, filepath):
    """make path to uploaded file (avatar/post) and adjust file name if needed
    note: used user id instead of instance (because it doesn't have it yet);
    return string(Unix-style: with / slashes) to MEDIA setting to form a final name
    """
    _date = date.today()
    date_trace = _date.strftime("%b_%d")
    filename = os.path.basename(filepath)  # 'abc.jpeg'
    name, ext = os.path.splitext(filename)  # tuple ('abc', '.jpeg')
    if len(name) > 5:
        name = name[:5] + "_"
    new_file_name = f"{name}_{file_generate_name(filepath)}"
    klass = (instance.__class__.__name__).lower()
    if klass == "profile":
        user_folder = f"profile_{instance.user.id}"
        return os.path.join("avatar", user_folder, new_file_name)
    elif klass == "post":
        folder = f"post_{date_trace}"
        return os.path.join("post", folder, new_file_name)
    elif klass == "image":
        folder = f"post_{date_trace}"
        return os.path.join("post", folder, new_file_name)
    elif klass == "category":
        return os.path.join("category", new_file_name)
    elif klass == "video":
        return os.path.join("video", new_file_name)
    elif klass == "imagecollection":
        return os.path.join("imagecollection", new_file_name)
    else:
        return os.path.join("extra", new_file_name)


def show_comment_form(update_time):
    """help func to compare post update and current time"""
    utc = pytz.UTC
    today = utc.localize(datetime.now())

    add_100_days = update_time + timedelta(days=100)
    return today > add_100_days


def get_temporary_text_file():
    """help func for testing"""
    file = SimpleUploadedFile(
        "test_image.txt", content=b"text_file", content_type="text/txt"
    )
    file.seek(0)
    return file


def get_temporary_image():
    """help func for testing in views: SimpleUpload"""
    file = io.BytesIO()
    image = Image.new("RGBA", size=(200, 200), color=(255, 0, 0, 0))
    image.save(file, format="png")
    img_file = SimpleUploadedFile("iop.png", file.getvalue())
    img_file.seek(0)
    return img_file


def get_temp_img_bytes():
    """help func for testing in webtest: just bytes;
    cannot write mode RGBA as JPEG!"""
    _file = io.BytesIO()
    img = Image.new("RGB", size=(20, 20), color=(255, 0, 0))
    img.save(_file, format="JPEG")
    _bytes = _file.getvalue()
    return _bytes


def parse_path(request):
    return request.path_info.strip("/").split("/")[0]
