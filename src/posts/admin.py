from django.contrib import admin, messages
from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from django.utils.translation import ngettext
from django_ckeditor_5.widgets import CKEditor5Widget
from modeltranslation.admin import TranslationAdmin
from treebeard.admin import TreeAdmin
from treebeard.forms import movenodeform_factory

from src.contacts.models import NewsLetter
from src.core.utils.admin_help import admin_link
from src.posts.filters import SoftDelFilter
from src.posts.models.categ_model import Category
from src.posts.models.media_model import ImageCollection, Video
from src.posts.models.post_model import Post


@admin.register(Category)
class CategoryAdmin(TreeAdmin, TranslationAdmin):
    form = movenodeform_factory(Category)
    list_display = ["name", "slug"]
    ordering = ["path"]


class PicsInline(admin.TabularInline):
    model = Post.pics.through
    extra = 1
    classes = ["collapse"]


@admin.register(ImageCollection)
class ImageCollection(admin.ModelAdmin):
    inlines = [
        PicsInline,
    ]
    list_display = ["id", "title", "display_posts"]

    def display_posts(self, obj):
        """if posts make a flat list of them"""
        posts_list = obj.posts.all().values_list("title", flat=True)
        return ",".join(posts_list)


@admin.register(Post)
class PostAdmin(TranslationAdmin):
    """
    author field for current user;
    user== staff AND group devs can crud only their own objects;
    alert: no auto-create published_at!
    """

    inlines = [
        PicsInline,
    ]

    exclude = ["pics"]

    date_hierarchy = "created_at"
    search_fields = ("title", "categ__name")

    list_display = [
        # "id",
        "short_title",
        "pub_date",
        "status",
        "is_deleted",
        "send_status",
        "show_img",
        "display_tags",
        "categ_link",
        "letter",
        "count_likes",
    ]
    list_select_related = ("categ", "author")
    list_editable = ["is_deleted"]
    list_display_links = ["short_title"]
    list_filter = ["status", "created_at"]
    radio_fields = {"status": admin.HORIZONTAL}
    save_on_top = True
    list_filter = ["status", "created_at", SoftDelFilter, "send_status"]
    list_per_page = 15
    actions = ("make_posts_published", "set_to_draft")
    empty_value_display = "#"
    formfield_overrides = {
        models.TextField: {"widget": CKEditor5Widget(config_name="extends")},
    }
    fieldsets = [
        (
            None,
            {
                "fields": [
                    "author",
                    "title_ru",
                    "content_ru",
                    "status",
                    "published_at",
                    "categ",
                    "top_img",
                    "url_top_img",
                    "allow_comments",
                    "is_deleted",
                    "featured",
                    "tags",
                    "send_status",
                ],
            },
        ),
        (
            "Не забудь про новостное письмо",
            {
                "classes": ["collapse"],
                "fields": [
                    "letter",
                    "title_en",
                    "title_uk",
                    "content_en",
                    "content_uk",
                    "video",
                ],
            },
        ),
    ]

    @admin.action(description="to_public")
    def make_posts_published(self, request, queryset):
        """make possbile to mark posts as published in admin bar checkbox"""
        updated = queryset.update(status=2, published_at=timezone.now())
        self.message_user(
            request,
            ngettext(
                "%d post successfully marked as published.",
                "%d posts were successfully marked as published.",
                updated,
            )
            % updated,
            messages.SUCCESS,
        )

    @admin.action(description="to_review")
    def set_to_review(self, request, queryset):
        """make possbile to mark posts as published in admin bar checkbox"""
        updated = queryset.update(status=1, published_at=timezone.now())

        self.message_user(
            request,
            ngettext(
                "%d post successfully marked as published.",
                "%d posts were successfully marked as published.",
                updated,
            )
            % updated,
            messages.SUCCESS,
        )

    @admin.action(description="to_draft")
    def set_to_draft(self, request, queryset):
        """make possbile to undo published status"""
        updated = queryset.update(status=0, published_at=None)

        self.message_user(
            request,
            ngettext(
                "%d post successfully marked as draft.",
                "%d posts were successfully marked as draft.",
                updated,
            )
            % updated,
            messages.WARNING,
        )

    def get_queryset(self, request):
        """
        super user can crud all posts;
        user is_staff can crud only their own objetcs
        """
        initial_qs = super().get_queryset(request).prefetch_related("tags")
        dev_group = get_user_model().objects.filter(groups__name="devs")
        if request.user.is_superuser:
            return initial_qs
        elif request.user.is_staff and (request.user in dev_group):
            return initial_qs.filter(author=request.user)

    def show_img(self, obj):
        """if top_img show small thumbnail in admin table"""
        if obj.top_img:
            return format_html("<img src={} width='60' />", obj.top_img.url)

    def pub_date(self, obj):
        """if top_img show small thumbnail in admin table"""
        if obj.published_at:
            return obj.published_at.strftime("%d/%m/%Y")

    def display_tags(self, obj):
        """if tags make a flat list of them"""
        tags_list = obj.tags.all().values_list("name", flat=True)
        return ", ".join(tags_list)

    def short_title(self, obj):
        """shortcut title"""
        return obj.title[:20]

    # new feature: adjust admin (see three func below)
    # current admin will be auto-selected in add post view
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """
        update admin kwargs
        create/edit post:  FK models в drop-down
        """
        if db_field.name == "author":
            # drop-down only with current user
            kwargs["queryset"] = get_user_model().objects.filter(
                username=request.user.username
            )
        if db_field.name == "letter":
            # drop-down only with letters (status = ready_to_send)
            kwargs["queryset"] = NewsLetter.objects.filter(letter_status=1)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def get_readonly_fields(self, request, obj=None):
        """
        создание новой статьи или edit post page:
        drop-down будет содержать только 1 опцию: current user(author)
        """
        if obj is not None:
            return self.readonly_fields + ("author",)  # , "letter")
        return self.readonly_fields

    def add_view(self, request, form_url="", extra_context=None):
        """newletter only last obj with status ready-to-send"""
        data = request.GET.copy()
        data["author"] = request.user
        data["letter"] = NewsLetter.objects.filter(letter_status=1).last()
        request.GET = data
        return super().add_view(request, form_url="", extra_context=extra_context)

    # new feature: adjust admin (see two func below)
    # using link to access related categ object

    @admin_link("categ", _("Категория"))
    def categ_link(self, categ: object):
        return categ

    @admin_link("letter", _("Letter"))
    def letter_link(self, letter: object):
        return letter

    def formfield_for_choice_field(self, db_field, request, **kwargs):
        """
        selection drop-down widget(FK obj)
        """

        if db_field.name == "status":
            select_items = db_field.choices
            kwargs["choices"] = select_items
        if db_field.name == "send_status":
            select_items = db_field.choices
            kwargs["choices"] = select_items
        return super().formfield_for_choice_field(db_field, request, **kwargs)

    def get_action_choices(self, request):
        """List UI: remove --- in dropdown choices"""
        choices = super().get_action_choices(request)
        choices.pop(0)
        return choices

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser


@admin.register(Video)
class Video(admin.ModelAdmin):
    list_display = ["id", "url", "show_thumb"]

    def show_thumb(self, obj):
        """if top_img show small thumbnail in admin table"""
        if obj.thumbnail:
            return format_html("<img src={} width='60' />", obj.thumbnail.url)
