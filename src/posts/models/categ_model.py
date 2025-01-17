from autoslug import AutoSlugField
from django.db import models
from django.utils.translation import gettext_lazy as _
from treebeard.mp_tree import MP_Node

from src.core.utils.base import upload_img


class Category(MP_Node):
    name = models.CharField(max_length=40, unique=True)
    slug = AutoSlugField(populate_from="name", unique=True)
    icon = models.ImageField(null=True, blank=True, upload_to=upload_img)

    node_order_by = ["name"]

    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"

    @classmethod
    def get_default_pk(cls, *args, **kwargs):
        """create or use existed default category"""
        qs = cls.objects.filter(
            name_ru=_("Неопределена"), name_uk="Невизначений", name_en="Unspecified"
        )
        try:
            obj = qs.get()
        except qs.model.DoesNotExist:
            cls.add_root(
                name_ru="Неопределена", name_uk="Невизначений", name_en="Unspecified"
            )
            obj = cls.objects.filter(
                name_ru="Неопределена", name_uk="Невизначений", name_en="Unspecified"
            ).last()

        return obj.pk

    def get_full_path(self):
        if self.is_root():
            path_slug = self.slug
        else:
            path_slug = "/".join(
                list(self.get_ancestors().values_list("slug", flat=True))
            )
            path_slug += f"/{self.slug}"
        return path_slug

    def get_name_slug_chain(self) -> dict:
        """
        create dict of name(s)/slug(s) of a given category
        incl ancestors
        """
        if self.is_root():
            path_name = self.name
            path_slug = self.slug

        else:
            path_name = "/".join(
                list(self.get_ancestors().values_list("name", flat=True))
            )
            path_name += f"/{self.name}"
            path_slug = "/".join(
                list(self.get_ancestors().values_list("slug", flat=True))
            )
            path_slug += f"/{self.slug}"

        return {"path_name": path_name, "path_slug": path_slug}

    def __str__(self):
        return self.name
