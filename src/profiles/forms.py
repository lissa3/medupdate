import logging

from django.conf import settings
from django.core.files.uploadedfile import InMemoryUploadedFile, TemporaryUploadedFile
from django.forms import ClearableFileInput, ImageField, ModelForm, ValidationError
from django.template.defaultfilters import filesizeformat
from django.utils.translation import gettext_lazy as _

from src.core.utils.resize import resize

from .models import Profile

logger = logging.getLogger("upload")


class MyClearableFileInput(ClearableFileInput):
    """adjust default clear attr"""

    clear_checkbox_label = _("Remove current image")
    initial_text = ""
    input_text = _("Change Image")
    template_name = "widgets/clear_image_input.html"

    def __init__(self, *args, **kwargs):
        """add acceptable file types"""
        super().__init__(*args, **kwargs)
        self.attrs.update({"accept": settings.UPLOAD_FILE_TYPES})


class CustomUploadImageField(ImageField):
    """
    let op: first check on the client side(ext and size 100KB)
    """

    # default_error_messages
    custom_error_messages = {
        "min_size": _("Uploaded file should not be less than %(size)s."),
        "max_size": _("Uploaded file should not be more than %(size)s"),
        "file_type": _("Uploaded file should have format: jpeg, jpg or png"),
    }

    def widget_attrs(self, widget):
        attrs = super().widget_attrs(widget)
        attrs.update({"accept": settings.UPLOAD_FILE_TYPES})
        return attrs

    def clean(self, *args, **kwargs):
        up_file = super().clean(*args, **kwargs)
        if isinstance(up_file, InMemoryUploadedFile) or isinstance(
            up_file, TemporaryUploadedFile
        ):
            err_msg = self.custom_error_messages
            min_upload_size = settings.MIN_UPLOAD_SIZE
            max_upload_size = settings.MAX_UPLOAD_SIZE
            file_types = settings.UPLOAD_FILE_TYPES

            if up_file.content_type not in file_types.split(","):
                logger.warning("extention is not allowed")
                raise ValidationError(err_msg["file_type"])
            if up_file.size < min_upload_size:
                raise ValidationError(
                    err_msg["min_size"],
                    params={"size": filesizeformat(min_upload_size)},
                )
            if up_file.size > max_upload_size:
                logger.warning("unploaded file to large")
                raise ValidationError(
                    err_msg["max_size"],
                    params={"size": filesizeformat(max_upload_size)},
                )

        return up_file


class ProfileForm(ModelForm):
    IMAGE_WIDTH = 300
    IMAGE_HEIGHT = 300

    avatar = CustomUploadImageField(
        required=False,
        help_text=_("Size not more than 2 MB; format:png/jpeg/jpg"),
        widget=MyClearableFileInput(),
    )

    class Meta:
        model = Profile
        fields = ["avatar"]

    def clean_avatar(self):
        image = self.cleaned_data.get("avatar")
        avatar = resize(image, self.IMAGE_WIDTH, self.IMAGE_HEIGHT)
        return avatar
