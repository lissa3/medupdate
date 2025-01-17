from django.contrib import admin

from .models import NewsLetter


@admin.register(NewsLetter)
class NewsLetterAdmin(admin.ModelAdmin):
    """
    after sending letter status as well as
    related posts status should be changd
    """

    date_hierarchy = "added_at"
    search_fields = ("title", "letter_status")

    list_display = ["id", "short_title", "letter_status", "date_sent"]
    list_display_links = ["id", "short_title"]
    list_filter = ["added_at", "letter_status"]
    save_on_top = True
    list_per_page = 15

    def display_tags(self, obj):
        """if tags make a flat list of them"""
        tags_list = obj.tags.all().values_list("name", flat=True)
        return ", ".join(tags_list)

    def short_title(self, obj):
        """shortcut title"""
        return obj.title[:20]
