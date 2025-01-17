from django.db import models


class TimeStamp(models.Model):
    """it is abstract diff models"""

    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)

    class Meta:
        abstract = True


class MediaStamp(models.Model):
    """it is abstract for Image and Video models"""

    title = models.CharField(max_length=255, default="", blank=True)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-added_at"]
        abstract = True

    def __str__(self) -> str:
        return self.title

    def get_image_basedir(self, some_dir):
        return f"/{some_dir}"
